from pathlib import Path
from app.repositories.storage_base import Storage
from app.schemas.paymentSchema import SavedPaymentMethod


class PaymentMethodStorage(Storage[dict]):
    """
    Persists saved payment methods keyed by user_id.
    Structure:
      {
        "<user_id>": {
            "<method_id>": { ...SavedPaymentMethod fields... },
            ...
        }
      }
    """

    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent / "data" / "paymentMethods.json"
        super().__init__(path)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _user_key(self, user_id: int) -> str:
        return str(user_id)

    def _get_user_methods(self, user_id: int) -> dict:
        data = self.read(self._user_key(user_id))
        return data if data is not None else {}

    def _save_user_methods(self, user_id: int, methods: dict) -> None:
        self.write(self._user_key(user_id), methods)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def get_all_methods(self, user_id: int) -> list[SavedPaymentMethod]:
        methods = self._get_user_methods(user_id)
        return [SavedPaymentMethod(**v) for v in methods.values()]

    def get_method(self, user_id: int, method_id: str) -> SavedPaymentMethod | None:
        methods = self._get_user_methods(user_id)
        entry = methods.get(method_id)
        return SavedPaymentMethod(**entry) if entry else None

    def save_method(self, user_id: int, method: SavedPaymentMethod) -> SavedPaymentMethod:
        methods = self._get_user_methods(user_id)

        # If this is the first card, make it default automatically
        if not methods:
            method.is_default = True

        methods[method.method_id] = method.model_dump(mode="json")
        self._save_user_methods(user_id, methods)
        return method

    def delete_method(self, user_id: int, method_id: str) -> bool:
        methods = self._get_user_methods(user_id)
        if method_id not in methods:
            return False
        del methods[method_id]
        self._save_user_methods(user_id, methods)
        return True

    def set_default(self, user_id: int, method_id: str) -> bool:
        methods = self._get_user_methods(user_id)
        if method_id not in methods:
            return False
        for mid, m in methods.items():
            m["is_default"] = (mid == method_id)
        self._save_user_methods(user_id, methods)
        return True

    def get_default_method(self, user_id: int) -> SavedPaymentMethod | None:
        for m in self.get_all_methods(user_id):
            if m.is_default:
                return m
        return None
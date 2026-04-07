from pathlib import Path
from app.repositories.storage_base import Storage
from app.schemas.paymentSchema import SavedPaymentMethod

class PaymentMethodStorage(Storage[dict]):
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent / "data" / "paymentMethods.json"
        super().__init__(path)

    def _user_key(self, username: str) -> str:
        # Key is now the username string (was int user_id before)
        return username

    def _get_user_methods(self, username: str) -> dict:
        data = self.read(self._user_key(username))
        return data if data is not None else {}

    def _save_user_methods(self, username: str, methods: dict) -> None:
        self.write(self._user_key(username), methods)

    def get_all_methods(self, username: str) -> list[SavedPaymentMethod]:
        methods = self._get_user_methods(username)
        return [SavedPaymentMethod(**v) for v in methods.values()]

    def get_method(self, username: str, method_id: str) -> SavedPaymentMethod | None:
        methods = self._get_user_methods(username)
        entry = methods.get(method_id)
        return SavedPaymentMethod(**entry) if entry else None

    def save_method(self, username: str, method: SavedPaymentMethod) -> SavedPaymentMethod:
        methods = self._get_user_methods(username)

        if not methods:
            method.is_default = True

        methods[method.method_id] = method.model_dump(mode="json")
        self._save_user_methods(username, methods)
        return method

    def delete_method(self, username: str, method_id: str) -> bool:
        methods = self._get_user_methods(username)
        if method_id not in methods:
            return False
        del methods[method_id]
        self._save_user_methods(username, methods)
        return True

    def set_default(self, username: str, method_id: str) -> bool:
        methods = self._get_user_methods(username)
        if method_id not in methods:
            return False
        for mid, m in methods.items():
            m["is_default"] = (mid == method_id)
        self._save_user_methods(username, methods)
        return True

    def get_default_method(self, username: str) -> SavedPaymentMethod | None:
        for m in self.get_all_methods(username):
            if m.is_default:
                return m
        return None
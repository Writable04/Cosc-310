# import pytest
# from pathlib import Path
# from app.repositories.menu_repo import MenuStorage
# from app.schemas.menuSchema import Menu


# @pytest.fixture
# def storage(tmp_path):
#     test_file = tmp_path / "menus.csv"
#     return MenuStorage(path=test_file)


# @pytest.fixture
# def sample_menu():
#     return Menu.model_construct(
#         menu_id=1,
#         itemList="[]"
#     )


# def test_new_menu(storage, sample_menu):
#     result = storage.new_menu(sample_menu)

#     rows = storage.read_all()

#     assert result.menu_id == 1
#     assert len(rows) == 1
#     assert rows[0]["menu_id"] == "1"


# def test_find_menu(storage, sample_menu):
#     storage.new_menu(sample_menu)

#     rows = storage.read_all()

#     assert len(rows) == 1
#     assert rows[0]["menu_id"] == "1"


# def test_update_menu(storage, sample_menu):
#     storage.new_menu(sample_menu)

#     storage.update("menu_id", 1, {"menu_id": "1"})

#     rows = storage.read_all()
#     assert len(rows) == 1
#     assert rows[0]["menu_id"] == "1"


# def test_remove_menu(storage, sample_menu):
#     storage.new_menu(sample_menu)

#     storage.delete("menu_id", 1)

#     rows = storage.read_all()
#     assert rows == []
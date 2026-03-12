from fastapi import APIRouter
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.services.dataset.dataset import getItemList
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.menu_repo import MenuStorage
from app.repositories.item_repo import ItemStorage


router = APIRouter()

resturants = []
menus = []
items = []

res = ResturantStorage()
me = MenuStorage()
it = ItemStorage()

#resturants
@router.post("/postResturant")
def post_resturant(resturant: Resturant):
    resturants.append(resturant.dict())
    res.new_resturant(resturant)
    return resturants

@router.get("/getResturant/{restaurant_id}", response_model=Resturant)
def get_resturant(restaurant_id: int):
    return res.find_resturant(resturant_id)

@router.put("/setResturant/{restaurant_id}")
def setResturant(restaurant_id: int, resturant: Resturant):
    res.update_resturant(restaurant_id, resturant.dict())
    return resturant.dict()

@router.delete("/removeResturant/{restaurant_id}")
def removeRestaurant(restaurant_id: int):
    res.remove_resturant(restaurant_id)
    return resturants

#menus
@router.post("/postMenu")
def post_menu(menu: Menu):
    menus.append(menu.dict())
    me.new_menu(menu)
    return menus

@router.get("/getMenu/{menu_id}", response_model=Menu)
def get_menu(menu_id: int):
    return res.find_menu(menu_id)

@router.put("/setMenu/{menu_id}")
def setMenu(menu_id: int, menu: Menu):
    me.update_menu(menu_id, menu.dict())
    return menu.dict()

@router.delete("/removeMenu/{menu_id}")
def removeMenu(menu_id: int):
    me.remove_menu(menu_id)
    return menus

#items
@router.post("/postItem")
def post_item(item: Item):
    items.append(item.dict())
    it.new_item(item)
    return items

@router.get("/getItem/{item_id}", response_model=Item)
def get_item(item_id: int):
    return it.find_item(item_id)

@router.put("/setItem/{item_id}")
def setItem(item_id: int, item: Item):
    it.update_item(item_id, item.dict())
    return item.dict()

@router.delete("/removeItem/{item_id}")
def removeItem(item_id: int):
    it.remove_item(item_id)
    return items
from fastapi import APIRouter
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.routers.dependencies import resturant_storage, menu_storage, item_storage

router = APIRouter()

resturants = []
menus = []
items = []

#resturants
@router.post("/restaurant")
def post_resturant(restaurant: Resturant):
    resturants.append(restaurant.dict())
    resturant_storage.new_resturant(restaurant)
    return resturants

@router.get("/restaurant/{restaurant_id}", response_model=Resturant)
def get_resturant(restaurant_id: int):
    return resturant_storage.find_resturant(restaurant_id)

@router.put("/restaurant/{restaurant_id}")
def setResturant(restaurant_id: int, resturant: Resturant):
    resturant_storage.update_resturant(restaurant_id, resturant.dict())
    return resturant.dict()

@router.delete("/restaurant/{restaurant_id}")
def removeRestaurant(restaurant_id: int):
    resturant_storage.remove_resturant(restaurant_id)
    return resturants

#menus
@router.post("/menu")
def post_menu(menu: Menu):
    menus.append(menu.dict())
    menu_storage.new_menu(menu)
    return menus

@router.get("/menu/{menu_id}", response_model=Menu)
def get_menu(menu_id: int):
    return me.find_menu(menu_id)

@router.put("/menu/{menu_id}")
def setMenu(menu_id: int, menu: Menu):
    menu_storage.update_menu(menu_id, menu.dict())
    return menu.dict()

@router.delete("/menu/{menu_id}")
def removeMenu(menu_id: int):
    menu_storage.remove_menu(menu_id)
    return menus

#items
@router.post("/item")
def post_item(item: Item):
    items.append(item.dict())
    item_storage.new_item(item)
    return items

@router.get("/item/{item_id}", response_model=Item)
def get_item(item_id: int):
    return item_storage.find_item(item_id)

@router.put("/item/{item_id}")
def setItem(item_id: int, item: Item):
    item_storage.update_item(item_id, item.dict())
    return item.dict()

@router.delete("/item/{item_id}")
def removeItem(item_id: int):
    item_storage.remove_item(item_id)
    return items
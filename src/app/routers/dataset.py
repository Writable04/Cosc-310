from fastapi import APIRouter, Depends
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.routers.dependencies import require_auth, resturant_storage, menu_storage, item_storage, accounts_storage

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

@router.get("/restaurants/{username}/{token}", response_model=list[Resturant], dependencies=[Depends(require_auth)])
def get_resturants(username: str):
    resturants = resturant_storage.read_all()
    user_address = accounts_storage.get_address(username)

    if user_address is None or user_address == "":
        return [Resturant(**resturant) for resturant in resturants]

    resturants_with_distances = []
    for resturant in resturants:
        data = Resturant(**resturant)
        dist, duration = resturant_storage.get_restaurant_distances(data.restaurant_id, user_address)
        data.durationNinutes = duration
        data.distanceKM = dist
        resturants_with_distances.append(data)

    return resturants_with_distances

@router.get("/restaurant/{restaurant_id}/{username}/{token}", response_model=Resturant, dependencies=[Depends(require_auth)])
def get_resturant(restaurant_id: int, username: str):
    user_address = accounts_storage.get_address(username)
    return resturant_storage.find_resturant(restaurant_id, user_address)

@router.put("/restaurant/{restaurant_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def setResturant(restaurant_id: int, resturant: Resturant):
    resturant_storage.update_resturant(restaurant_id, resturant.dict())
    return resturant.dict()

@router.delete("/restaurant/{restaurant_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def removeRestaurant(restaurant_id: int):
    resturant_storage.remove_resturant(restaurant_id)
    return resturants

#menus
@router.post("/menu/{username}/{token}", dependencies=[Depends(require_auth)])
def post_menu(menu: Menu):
    menus.append(menu.dict())
    menu_storage.new_menu(menu)
    return menus

@router.get("/menu/{menu_id}/{username}/{token}", response_model=Menu, dependencies=[Depends(require_auth)])
def get_menu(menu_id: int):
    return menu_storage.find_menu(menu_id)

@router.put("/menu/{menu_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def setMenu(menu_id: int, menu: Menu):
    menu_storage.update_menu(menu_id, menu.dict())
    return menu.dict()

@router.delete("/menu/{menu_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def removeMenu(menu_id: int):
    menu_storage.remove_menu(menu_id)
    return menus

#items
@router.post("/item/{username}/{token}", dependencies=[Depends(require_auth)])
def post_item(item: Item):
    items.append(item.dict())
    item_storage.new_item(item)
    return items

@router.get("/item/{item_id}/{username}/{token}", response_model=Item, dependencies=[Depends(require_auth)])
def get_item(item_id: int):
    return item_storage.find_item(item_id)

@router.put("/item/{item_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def setItem(item_id: int, item: Item):
    item_storage.update_item(item_id, item.dict())
    return item.dict()

@router.delete("/item/{item_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def removeItem(item_id: int):
    item_storage.remove_item(item_id)
    return items
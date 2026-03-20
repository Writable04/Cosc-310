from fastapi import APIRouter, HTTPException
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.routers.dependencies import resturant_storage, menu_storage, item_storage
from app.services.dataset.dataset import assign_restaurant_id
router = APIRouter()

resturants = []
menus = []
items = []

#resturants
@router.post("/restaurant")
def post_resturant(restaurant: Resturant):
    try:
        resturants.append(restaurant.dict())
        restaurant = assign_restaurant_id(restaurant, resturant_storage)
        resturant_storage.new_resturant(restaurant)
        return resturants

    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/restaurant/{restaurant_id}", response_model=Resturant)
def get_resturant(restaurant_id: int):
    try:
        return resturant_storage.find_resturant(restaurant_id)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.put("/restaurant/{restaurant_id}")
def setResturant(restaurant_id: int, resturant: Resturant):
    try:
        resturant_storage.update_resturant(restaurant_id, resturant.dict())
        return resturant.dict()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.delete("/restaurant/{restaurant_id}")
def removeRestaurant(restaurant_id: int):
    try:
        resturant_storage.remove_resturant(restaurant_id)
        return resturants
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

#menus
@router.post("/menu")
def post_menu(menu: Menu):
        c = menu_storage.new_menu(menu)
        return c
    
@router.get("/menu/{menu_id}", response_model=Menu)
def get_menu(menu_id: int):
    try:
        return menu_storage.find_menu(menu_id)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.put("/menu/{menu_id}")
def setMenu(menu_id: int, menu: Menu):
    try:
        menu_storage.update_menu(menu_id, menu.dict())
        return menu.dict()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.delete("/menu/{menu_id}")
def removeMenu(menu_id: int):
    try:
        menu_storage.remove_menu(menu_id)
        return menus
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

#items
@router.post("/item")
def post_item(item: Item):
    try:
        items.append(item.dict())
        item_storage.new_item(item)
        return items
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/item/{item_id}", response_model=Item)
def get_item(item_id: int):
    try:
        return item_storage.find_item(item_id)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))
    

@router.put("/item/{item_id}")
def setItem(item_id: int, item: Item):
    try:
        item_storage.update_item(item_id, item.dict())
        return item.dict()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.delete("/item/{item_id}")
def removeItem(item_id: int):
    try: 
        item_storage.remove_item(item_id)
        return items
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))
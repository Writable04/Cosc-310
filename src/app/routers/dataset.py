from fastapi import APIRouter, Depends, HTTPException
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.routers.dependencies import require_auth, resturant_storage, menu_storage, item_storage, accounts_storage
from app.services.dataset.dataset import assign_restaurant_id
router = APIRouter()

resturants = []
menus = []
items = []

#resturants
@router.post("/restaurant/{username}/{token}", dependencies=[Depends(require_auth)])
def post_resturant(restaurant: Resturant):
    try:
        resturants.append(restaurant.dict())
        restaurant = assign_restaurant_id(restaurant, resturant_storage)
        resturant_storage.new_resturant(restaurant)
        return resturants

    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/restaurants/{username}/{token}", response_model=list[Resturant], dependencies=[Depends(require_auth)])
def get_resturants(username: str):
    resturants = resturant_storage.read_all()
    user_address = accounts_storage.get_address(username)

    if user_address is None or user_address == "":
        return [Resturant(**resturant) for resturant in resturants]

    return resturant_storage.get_resturants_with_distances(user_address)

@router.get("/restaurant/{restaurant_id}/{username}/{token}", response_model=Resturant, dependencies=[Depends(require_auth)])
def get_resturant(restaurant_id: int, username: str):
    try:
        user_address = accounts_storage.get_address(username)
        return resturant_storage.find_resturant(restaurant_id, user_address)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.put("/restaurant/{restaurant_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def setResturant(restaurant_id: int, resturant: Resturant):
    try:
        resturant_storage.update_resturant(restaurant_id, resturant.dict())
        return resturant.dict()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.delete("/restaurant/{restaurant_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def removeRestaurant(restaurant_id: int):
    try:
        resturant_storage.remove_resturant(restaurant_id)
        return resturants
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

#menus
@router.post("/menu/{username}/{token}", dependencies=[Depends(require_auth)])
def post_menu(menu: Menu):
    try:
        menus.append(menu.dict())
        menu_storage.new_menu(menu)
        return menus
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.get("/menu/{menu_id}/{username}/{token}", response_model=Menu, dependencies=[Depends(require_auth)])
def get_menu(menu_id: int):
    try:
        return menu_storage.find_menu(menu_id)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.put("/menu/{menu_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def setMenu(menu_id: int, menu: Menu):
    try:
        menu_storage.update_menu(menu_id, menu.dict())
        return menu.dict()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.delete("/menu/{menu_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def removeMenu(menu_id: int):
    try:
        menu_storage.remove_menu(menu_id)
        return menus
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

#items
@router.post("/item/{username}/{token}", dependencies=[Depends(require_auth)])
def post_item(item: Item):
    try:
        items.append(item.dict())
        item_storage.new_item(item)
        return items
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))


@router.get("/item/{item_id}/{username}/{token}", response_model=Item, dependencies=[Depends(require_auth)])
def get_item(item_id: int):
    try:
        return item_storage.find_item(item_id)
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))
    

@router.put("/item/{item_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def setItem(item_id: int, item: Item):
    try:
        item_storage.update_item(item_id, item.dict())
        return item.dict()
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

@router.delete("/item/{item_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def removeItem(item_id: int):
    try: 
        item_storage.remove_item(item_id)
        return items
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error))

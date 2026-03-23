from pathlib import Path
from app.schemas.cartSchema import Cart, CartItem
from app.repositories.storage_base import Storage
from app.repositories.item_repo import ItemStorage
from app.repositories.resturant_repo import ResturantStorage

class CartStorage(Storage[Cart]):
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent/"data"/"cartData"/"cart.json"
        super().__init__(path)

    def loadUserCart(self, username: str) -> Cart | None:
        data = self.read(username)
        if data is None:
            emptyCart = Cart(user_id=username, restaurant="", items=[], subtotal=0.00)
            self.write(username, emptyCart.model_dump(mode="json"))
            return Cart.model_validate(emptyCart)
        else:
            return Cart.model_validate(data)

    def clearUserCart(self, username: str) -> Cart | None:
        data = self.read(username)
        if data is not None:
            emptyCart = Cart(user_id=username, restaurant="", items=[], subtotal=0.00)
            self.write(username, emptyCart.model_dump(mode="json"))

    def removeCart(self, username: str):
        theCart = self.read(username)
        del theCart

    def addItem(self, username: str, itemID: int):
        # check if the item is already in the cart --if yes> increase quantity by one
        theCart = self.read(username)
        theItem = ItemStorage().find_item(itemID)

        if not theItem:
            return False

        found = False
        for item in theCart['items']:
            if item.get("itemID") == itemID:
                item["quantity"] += 1
                found = True 

        if (not found):
            newItem = CartItem(name=theItem.name, itemID=itemID, quantity = 1, price = theItem.price)
            theCart['items'].append(newItem.model_dump(mode="json"))
            
        CartStorage().updateCartRestaurant(theCart, theItem)  
        theCart['subtotal'] = CartStorage().updateSubtotal(theCart)
        self.write(username, theCart)
        return True

    def removeItem(self, username: str, itemID: int): # -> item
        # check if there is more than 1 object in the cart. if theres only one, remove the item entirely (delete the entry)
        theCart = self.read(username)
        theItem = ItemStorage().find_item(itemID)

        if not theItem:
            return False

        found = False
        for item in theCart['items']:
            if item.get("itemID") == itemID:
                if(item.get("quantity") > 1):
                    item["quantity"] -= 1
                else:
                    theCart['items'].remove(item)
                found = True
                break
                
        if (not found):
            return False
        
        CartStorage().updateCartRestaurant(theCart, theItem)  
        theCart['subtotal'] = CartStorage().updateSubtotal(theCart)
        self.write(username, theCart)
        return True


# COMPLEMENTARY FUNCTIONS (they are used within the above functions)
    def updateCartRestaurant(self, mrCart, mrItem):
        theRestaurant = ResturantStorage().find_resturant(mrItem.menu_id)
        resName = theRestaurant.name

        # if the cart is empty, clear restaruant name
        if mrCart["items"] == []:
            mrCart['restaurant'] = ""
            return
        
        # if restaurant hasnt been established 
        elif mrCart['restaurant'] == "" :
            mrCart['restaurant'] = resName
            return

        # if it already has the correct name
        elif mrCart['restaurant'] == resName:
            return
        
        #otherwise; if it has some other name
        else:
            # YOU SHOULD ONLY HAVE ONE RESTAURANT IN YOUR CART AT A TIME
            return(-1)
        
    def updateSubtotal(self, mrCart) -> float:
        mrSubtotal = 0.00
        for item in mrCart['items']:
            mrSubtotal += (item["quantity"])*(item["price"])
        # IMPLEMENT COMBO DISCOUNTS!!!

        return round(mrSubtotal, 2)
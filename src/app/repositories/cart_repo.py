from pathlib import Path
from app.schemas.cartSchema import Cart, CartItem
from app.repositories.storage_base import Storage
from app.repositories.item_repo import ItemStorage
from app.repositories.menu_repo import MenuStorage

class CartStorage(Storage[Cart]):
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent/"data"/"cartData"/"cart.json"
        super().__init__(path)

    def loadUserCart(self, UserID) -> Cart | None:
        data = self.read(str(UserID))
        if data is None:
            emptyCart = Cart(user_id=UserID, restaurant="", items=[], subtotal=0.00)
            self.write(UserID, emptyCart.model_dump(mode="json"))
            return Cart.model_validate(emptyCart)
        else:
            return Cart.model_validate(data)

    def clearUserCart(self, UserID) -> Cart | None:
        data = self.read(str(UserID))
        if data is not None:
            emptyCart = Cart(user_id=UserID, restaurant="", items=[], subtotal=0.00)
            self.write(str(UserID), emptyCart.model_dump(mode="json"))

    def removeCart(self, UserID):
        theCart = self.read(str(UserID))
        del theCart

    def addItem(self, UserID, ItemID):
        # check if the item is already in the cart --if yes> increase quantity by one
        theCart = self.read(str(UserID))
        theItem = ItemStorage().find_item(ItemID)

        if not theItem:
            return False

        found = False
        for item in theCart['items']:
            if item.get("itemID") == ItemID:
                item["quantity"] += 1
                found = True
                #theCart.updateCartRestaurant(theCart, theItem, None)  

                
        if (not found):
            newItem = CartItem(name=theItem.name, itemID=ItemID, quantity = 1, price = theItem.price)
            theCart['items'].append(newItem.model_dump(mode="json"))

        theCart['subtotal'] = round((theCart['subtotal'] + float(theItem.price)), 2)
        self.write(str(UserID), theCart)
        return True

    def removeItem(self, UserID, ItemID): # -> item
        # check if there is more than 1 object in the cart. if theres only one, remove the item entirely (delete the entry)
        theCart = self.read(str(UserID))
        theItem = ItemStorage().find_item(ItemID)

        if not theItem:
            return False

        found = False
        for item in theCart['items']:
            if item.get("itemID") == ItemID:
                if(item.get("quantity") > 1):
                    item["quantity"] -= 1
                else:
                    theCart['items'].remove(item)
                found = True
                theCart['subtotal'] = round((theCart['subtotal'] - float(theItem.price)), 2)
                break
                
        if (not found):
            return False
        
        self.write(str(UserID), theCart)
        return True

    # THIS FUNCTION NEEDS TO BE UPDATED ONCE ITEM AND RESTAURANT ARE LINKED
    # def updateCartRestaurant(mrCart, mrItem, mrRestaurant) -> str:
    #     if mrCart['restaurant'] == "" :
    #         mrCart['restaurant'] = mrItem.menu_id
    #     elif mrCart['restaurant'] == mrItem.menu_id:
    #         return
    #     elif mrCart['restaurant'] is not mrItem.menu_id:
    #         # SEND NOTIFICATION THAT YOU SHOULD ONLY HAVE ONE RESTAURANT IN YOUR CART AT A TIME
    #         return("BAD RESTAURANT")
        
    # def updateSubtotal():
    #     # this function could update the subtotal by going thru all the entries
    #     # might be more secure than current implementation
    #     return None
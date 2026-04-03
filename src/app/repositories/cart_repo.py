from pathlib import Path
from app.schemas.cartSchema import Cart, CartItem
from app.repositories.storage_base import Storage
from app.repositories.item_repo import ItemStorage
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.menu_repo import MenuStorage

class CartStorage(Storage[Cart]):
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent/"data"/"cartData"/"cart.json"
        super().__init__(path)

    def loadUserCart(self, username: str) -> Cart:
        data = self.read(username)
        if data is None:
            emptyCart = Cart(
                user_id=username,
                restaurant="",
                items=[],
                subtotal=0.00,
                appliedCombos=[],
                totalDiscount=0.00,
                checkout_total=0.00
            )
            self.write(username, emptyCart.model_dump(mode="json"))
            return Cart.model_validate(emptyCart)
        else:
            return Cart.model_validate(data)

    def clearUserCart(self, username: str) -> bool:
        data = self.read(username)
        if data is not None:
            emptyCart = Cart(
                user_id=username,
                restaurant="",
                items=[],
                subtotal=0.00,
                appliedCombos=[],
                totalDiscount=0.00,
                checkout_total=0.00
            )
            emptyCart = Cart(user_id=username, restaurant="", items=[], subtotal=0.00)
            self.write(username, emptyCart.model_dump(mode="json"))
            return True
        

    def removeCart(self, username: str):
        theCart = self.read(username)
        CartStorage().clearUserCart(username)
        del theCart
        return True

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
        theCart['checkout_total'] = round(theCart['subtotal']- theCart['totalDiscount'],2)
        self.write(username, theCart)
        return True

    def removeItem(self, username: str, itemID: int):
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
        theCart['checkout_total'] = round(theCart['subtotal']- theCart['totalDiscount'],2)
        self.write(username, theCart)
        return True
    
    
    def addCombo(self, UserID, combo_id, menu_id):
        #adds combo to applied combos in cart and also adds combo items into items
        theCart = self.read(str(UserID))
        if theCart is None:
            return False

        # get menu 
        menu = MenuStorage().find_menu(menu_id)
        if not menu:
            return False

        target_combo = None
        for combo in menu.menuCombos:
            if combo.combo_id == combo_id:
                target_combo = combo
                break

        if not target_combo:
            return False

        for item_id in target_combo.comboItems:
            self.addItem(UserID, item_id)
        
        # updates cart for the addItem method checks
        theCart = self.read(str(UserID)) 
        
        found = False
        for combo in theCart["appliedCombos"]:
            if combo.get("combo_id") == combo_id:
                combo["quantity"] += 1
                found = True 
                break

        if (not found):
            new_combo = {
                "combo_id": target_combo.combo_id,
                "comboItems": target_combo.comboItems,
                "discountPrice": target_combo.discountPrice,
                "quantity": 1
            }
            theCart["appliedCombos"].append(new_combo)

        # update totals
        theCart['subtotal'] = self.updateSubtotal(theCart)
        
        discount = self.getTotalDiscount(theCart)
        theCart['totalDiscount'] = discount
        theCart['checkout_total'] = round(theCart['subtotal'] - discount, 2)

        self.write(str(UserID), theCart)
        return True

    
    def removeCombo(self, UserID, combo_id):
        theCart = self.read(str(UserID))
        if theCart is None:
            return False

        combos = theCart["appliedCombos"]

        found = False
        combo_items = []

        for combo in combos:
            if combo.get("combo_id") == combo_id:
                combo_items = combo.get("comboItems", [])

                if combo.get("quantity", 0) > 1:
                    combo["quantity"] -= 1
                else:
                    combos.remove(combo)

                found = True
                break

        if not found:
            return False


        for item_id in combo_items:
            self.removeItem(UserID, item_id)
        theCart = self.read(str(UserID))

        #makes sure that when single item gets removed combo gets adjusted (maybe move to seperate update function)

        valid_combos = []

        item_counts = {item["itemID"]: item["quantity"] for item in theCart["items"]}

        for combo in theCart.get("appliedCombos", []):
            max_possible_combos = min(item_counts.get(i, 0) for i in combo["comboItems"])
            
            if max_possible_combos > 0:
                combo["quantity"] = min(combo["quantity"], max_possible_combos)
                valid_combos.append(combo)

        theCart["appliedCombos"] = valid_combos

        #update totals
        theCart['subtotal'] = self.updateSubtotal(theCart)
        discount = self.getTotalDiscount(theCart)
        theCart['totalDiscount'] = discount
        theCart['checkout_total'] = round(self.updateCheckoutTotal, 2)

        self.write(str(UserID), theCart)
        return True
    
# COMPLEMENTARY FUNCTIONS (they are used within the above functions)

    def getTotalDiscount(self, theCart):
        total_discount = 0

        for combo in theCart.get("appliedCombos", []):
            quantity = combo.get("quantity", 0)
            discount_price = combo.get("discountPrice", 0.0)
            total_discount += discount_price * quantity

        return total_discount


# COMPLEMENTARY FUNCTIONS (they are used within the above functions)
    def updateCartRestaurant(self, mrCart, mrItem):
        theRestaurant = ResturantStorage().find_resturant(mrItem.menu_id)
        resName = theRestaurant.name

        # if the cart is empty, clear restaruant name
        if mrCart["items"] == []:
            mrCart['restaurant'] = ""
            return 1
        
        # if restaurant hasnt been established 
        elif mrCart['restaurant'] == "" :
            mrCart['restaurant'] = resName
            return 1

        # if it already has the correct name
        elif mrCart['restaurant'] == resName:
            return 1
        
        #otherwise; if it has some other name
        else:
            # YOU SHOULD ONLY HAVE ONE RESTAURANT IN YOUR CART AT A TIME
            return(-1)
        
    def updateSubtotal(self, mrCart) -> float:
        mrSubtotal = 0.00
        for item in mrCart['items']:
            mrSubtotal += (item["quantity"])*(item["price"])
        return round(mrSubtotal, 2)
    
    def updateCheckoutTotal(self, UserID):
        theCart = self.read(UserID)
        if not theCart:
            return 0.0
        
        subtotal = theCart["subtotal"]
        discount = self.getTotalDiscount(theCart)
        checkout_total = subtotal - discount

        theCart["checkout_total"] = round(checkout_total, 2)
        self.write(UserID, theCart)
        
        return checkout_total
    

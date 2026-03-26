from app.routers.dependencies import resturant_storage, menu_storage

def getComboDiscount(resName,mrCart):
        resturant = resturant_storage.find_resturant_query(resName, "name")
        if not resturant:
            return 0
        menu = menu_storage.find_menu(resturant.menu_id)
        if not menu:
            return 0
        
        #combos are the types of combos in a menu
        combos = menu.menuCombos

        #gets item ids within cart
        items = mrCart.get("items", [])
        cart_ids = [item["itemID"] for item in items]
        
        highestRate = 0
        for combo in combos:
            combo_items = combo.comboItems
            rate = combo.discountRate

            
            if all(ci in cart_ids for ci in combo_items):
                combo_price = sum(
                    item["price"]
                    for item in items
                    if item["itemID"] in combo_items
                )
                combo_count = min(
                    item["quantity"]
                    for item in items
                    if item["itemID"] in combo_items
                )

                discount = combo_count * combo_price * rate
                highestRate = max(highestRate, discount)        
        
        return highestRate
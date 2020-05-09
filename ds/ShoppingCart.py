class ShoppingCart:

    #
    # empty constructor
    #
    def __init__(self):
        self.purchases = []
        self.total_sum = 0

    #
    # Adds a Purchase object to the shopping cart
    #
    #
    def add_to_cart(self, purchase):
        # Update the total sum of the shopping cart
        self.total_sum += purchase.product.get_price() * purchase.count

        # Check cart if this product for this user is already in cart, if so update
        # Otherwise append the new purchase to the shopping cart list
        if not self.__find_duplicates(True, purchase):
            self.purchases.append(purchase)

        # return confirmation message
        return True

    #
    # Remove from shoppingcart
    #
    def remove_from_cart(self, purchase):
        # Check if the item is in the list
        if not self.__find_duplicates(False, purchase):
            return False

        else:
            # Update the total sum of the shopping cart
            self.total_sum -= purchase.product.get_price() * purchase.count
            return True

    # check for duplicates in purchase list
    #
    def __find_duplicates(self, add, purchase):
        # Iterate over all purchases currently stored in the shopping cart
        for p in self.purchases:
            # if the mail and product name matches, then we know there was an change of count
            # so we increment or decrement this field with @purchase.count
            if p.mail == purchase.mail and p.product == purchase.product:
                if add:
                    p.count = p.count + purchase.count
                else:
                    p.count = p.count - purchase.count
                    # If p.count has become zero, remove p completly from the list
                    if p.count == 0:
                        self.purchases.remove(p)
                # Shopping cart modified, return True as we do not need to append a new item to the list anymore
                return True
        # No item was found, append the item to the back of the list
        return False

    #
    # get shopping cart data
    #
    def get_shopping_cart(self):
        return self.purchases

    #
    # get total sum
    #
    def get_total_price(self):
        return self.total_sum
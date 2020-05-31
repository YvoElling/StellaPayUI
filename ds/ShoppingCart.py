import jsons as jsons


class ShoppingCart:

    #
    # empty constructor
    #
    def __init__(self):
        self.products = []

    #
    # Adds a Purchase object to the shopping cart
    #
    #
    def add_to_cart(self, purchase):
        # Check cart if this product for this user is already in cart, if so update
        # Otherwise append the new purchase to the shopping cart list
        if not self.__find_duplicates(True, purchase):
            self.products.append(purchase)

        # return confirmation message
        return True

    #
    # Remove from shoppingcart
    #
    def remove_from_cart(self, purchase):
        # Check if the item is in the list
        self.__find_duplicates(False, purchase)

    # check for duplicates in purchase list
    #
    def __find_duplicates(self, add, purchase):
        # Iterate over all purchases currently stored in the shopping cart
        for p in self.products:
            # if the mail and product name matches, then we know there was an change of count
            # so we increment or decrement this field with @purchase.count
            if p.email == purchase.email and p.product_name == purchase.product_name:
                if add:
                    p.amount = p.amount + 1
                else:
                    p.amount = p.amount - 1
                    # If p.count has become zero, remove p completely from the list
                    if p.amount == 0:
                        self.products.remove(p)
                # Shopping cart modified, return True as we do not need to append a new item to the list anymore
                return True
        # No item was found, append the item to the back of the list
        return False

    #
    # get shopping cart data
    #
    def get_shopping_cart(self):
        return self.products

    #
    # empty the shopping cart
    #
    def emtpy_cart(self):
        self.products = []

    #
    # implement json serializer
    #
    def to_json(self):
        return jsons.dump(self, default=lambda o: o.__dict__)

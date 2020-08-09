from typing import List, Optional

import jsons as jsons
from kivy import Logger

from ds.Purchase import Purchase


class ShoppingCart:

    #
    # empty constructor
    #
    def __init__(self):
        self.basket: List[Purchase] = []

    #
    # Adds a Purchase object to the shopping cart
    #
    #
    def add_to_cart(self, purchase: Purchase):
        # Check cart if this product for this user is already in cart, if so update
        # Otherwise append the new purchase to the shopping cart list
        duplicate = self.__find_duplicate(purchase)

        # We found a duplicate, so only update the duplicates amount
        if duplicate is not None:
            duplicate.amount += purchase.amount
        else:
            # No duplicate
            self.basket.append(purchase)

    #
    # Remove from shoppingcart
    #
    def remove_from_cart(self, purchase: Purchase):
        # Check if the item is in the list
        duplicate = self.__find_duplicate(purchase)

        # Check if the purchase actually exists
        if duplicate is not None:
            self.basket.remove(duplicate)
        else:
            Logger.warning("Tried to remove a purchase from the basket that was not present!")

    # Look for a duplicate purchase.
    def __find_duplicate(self, purchase: Purchase) -> Optional[Purchase]:
        # Iterate over all purchases currently stored in the shopping cart
        for p in self.basket:
            # if the mail and product name matches, then we know there was an change of count
            # so we increment or decrement this field with @purchase.count
            if p.purchaser_name == purchase.purchaser_name and p.product_name == purchase.product_name:
                return p
        return None

    #
    # get shopping cart data
    #
    def get_shopping_cart(self):
        return self.basket

    #
    # empty the shopping cart
    #
    def clear_cart(self):
        self.basket = []

    #
    # implement json serializer
    #
    def to_json(self):
        return jsons.dump(self, default=lambda o: o.__dict__)

from abc import abstractmethod, ABC
from typing import List, Optional

from kivy import Logger
from kivy.app import App

from ds.Purchase import Purchase


class ShoppingCartListener(ABC):
    @abstractmethod
    def on_change(self):
        pass


class ShoppingCart:

    #
    # empty constructor
    #
    def __init__(self):
        self.basket: List[Purchase] = []
        self.listeners: List[ShoppingCartListener] = []

    def add_listener(self, listener: ShoppingCartListener):
        self.listeners.append(listener)

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

        self.notify_listener()

    #
    # Remove from shoppingcart
    #
    def remove_from_cart(self, purchase: Purchase):
        # Check if the item is in the list
        duplicate = self.__find_duplicate(purchase)

        # Check if the purchase actually exists
        if duplicate is not None:
            if duplicate.amount == 1:
                self.basket.remove(duplicate)
            else:
                duplicate.amount -= purchase.amount
        else:

            Logger.warning("StellaPayUI: Tried to remove a purchase from the basket that was not present!")

        self.notify_listener()

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

        self.notify_listener()

    def notify_listener(self):
        for listener in self.listeners:
            listener.on_change()

    #
    # implement json serializer
    #
    def to_json(self):
        # Create JSON output variable as initial dictionary
        json_output = {"products": []}

        # Load all products into the dictionary.
        for purchase in self.basket:
            json_output["products"].append({
                # Look up the email address of the user that made the purchase
                "email": App.get_running_app().user_mapping[purchase.purchaser_name],
                "product_name": purchase.product_name,
                "amount": purchase.amount
            })

        return json_output

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

    def set_product_amount_in_cart(self, purchase: Purchase) -> None:
        """
        Set the amount for a specific product and user in the shopping cart. If the purchase doesn't exist yet,
        it will be added.
        :param purchase: Purchase information to set. If the amount is less than zero, the item will be removed from the
         shopping cart (if present).
        :return: Nothing
        """
        existing_purchase_item = self.__find_duplicate(purchase)

        # If it doesn't exist yet, add it to the car (if the amount is at least 1)
        if existing_purchase_item is None and purchase.amount > 0:
            self.add_to_cart(purchase)
        elif existing_purchase_item is not None:

            if purchase.amount <= 0:
                # We want to remove the existing purchase from the shopping cart
                self.basket.remove(existing_purchase_item)
            else:
                # We merely want to update the amount of current listing in the shopping car
                existing_purchase_item.amount = purchase.amount

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

    def get_amount_of_product(self, purchase: Purchase) -> int:
        """
        Get the amount of a product that is in this shopping cart for a specific user
        :param purchase: Purchase to look for (note that the amount is ignored)
        :return: the total amount of the given product for the given user in this shopping cart
        """
        existing_purchase = self.__find_duplicate(purchase)
        if existing_purchase is None:
            return 0
        return existing_purchase.amount

    # Look for a duplicate purchase.
    def __find_duplicate(self, purchase: Purchase) -> Optional[Purchase]:
        # Check for edge cases
        if purchase is None:
            return None

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
    def get_shopping_cart(self) -> List[Purchase]:
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

    @staticmethod
    def from_json(json_data) -> "ShoppingCart":
        shopping_cart = ShoppingCart()

        # If there is no JSON data, return an empty shopping car
        if json_data is None:
            return shopping_cart

        # If there are no products, we return an empty card again
        if "products" not in json_data:
            return shopping_cart

        for product in json_data["products"]:

            if product is None:
                continue

            email_address = product.get("email", None)
            product_name = product.get("product_name", None)
            amount = product.get("amount", 0)

            # This means it is not a valid product
            if email_address is None or product_name is None:
                continue

            # We don't care about products that have not at least one item
            if amount < 1:
                continue

            # Find the names that match this email-address
            names_matching_email = [name for name, email in App.get_running_app().user_mapping.items() if
                                    email == email_address]

            # We don't know who made the purchase
            if len(names_matching_email) < 1:
                continue

            product_to_register = Purchase(names_matching_email[0], product_name, amount)

            # Add product to caart
            shopping_cart.add_to_cart(product_to_register)

        return shopping_cart

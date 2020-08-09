from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem

from ds.Purchase import Purchase
from ds.ShoppingCart import ShoppingCart

Builder.load_file('kvs/PurchaserItem.kv')


class PurchaserItem(TwoLineAvatarIconListItem):

    # Set local member variables and forwards **kwargs to super class
    def __init__(self, product_name: str, shoppingcart: ShoppingCart, **kwargs):
        super(PurchaserItem, self).__init__(**kwargs)
        self.product = product_name
        self.shopping_cart = shoppingcart

        # Disable ripple effect
        self.ripple_scale = 0

    # Adds product to the shopping cart.
    def on_add_product(self):
        # Update count
        self.ids.count.text = str(int(self.ids.count.text) + 1)

        # Create purchase object
        purchase = Purchase(self.text, self.product, 1)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

    # Removes item from the shopping cart
    def on_remove_product(self):
        # Items can only be removed from the shopping cart when count > 0
        if int(self.ids.count.text) > 0:
            self.ids.count.text = str(int(self.ids.count.text) - 1)

            # Create purchase object (Default count = 1, due to plus button)
            purchase = Purchase(self.text, self.product, 1)

            # Remove product from the shopping cart
            self.shopping_cart.remove_from_cart(purchase)


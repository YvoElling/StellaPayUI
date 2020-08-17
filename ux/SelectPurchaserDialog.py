import time
from typing import List

from kivy.app import App
from kivymd.uix.dialog import MDDialog

from ds.Purchase import Purchase
from ds.ShoppingCart import ShoppingCart


class SelectPurchaserDialog(MDDialog):

    # Keep track of which product has been selected by the user
    selected_product = None

    def __init__(self, shopping_cart: ShoppingCart, **kwargs):
        super(SelectPurchaserDialog, self).__init__(**kwargs)
        self.shopping_cart = shopping_cart

    def on_add_product(self, purchaser_name: str):
        # Create purchase object
        purchase = Purchase(purchaser_name=purchaser_name, product_name=self.selected_product, count=1)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

    def on_remove_product(self, purchaser_name: str):
        # Create purchase object (Default count = 1, due to plus button)
        purchase = Purchase(purchaser_name=purchaser_name, product_name=self.selected_product, count=1)

        # Remove product from the shopping cart
        self.shopping_cart.remove_from_cart(purchase)

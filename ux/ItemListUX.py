import time
from typing import List

from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem

from ds.Purchase import Purchase
from ds.ShoppingCart import ShoppingCart
from ux.PurchaserItem import PurchaserItem

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    def __init__(self, price: str, shopping_cart: ShoppingCart, **kwargs):
        super(ItemListUX, self).__init__(**kwargs)

        # When the price is none of the shopping cart is none, this is a special edge case where we don't want the user to see the buttons
        if price is None or shopping_cart is None:
            # We set all the items of the screen to be invisible and disable the buttons.
            self.ids.price.opacity = 0
            self.ids.count.opacity = 0
            self.ids.plus.opacity = 0
            self.ids.plus.disabled = True
            self.ids.minus.opacity = 0
            self.ids.minus.disabled = True
            self.ids.other_user.opacity = 0
            self.ids.other_user.disabled = True
        else:
            self.ids.price.text = price

        if shopping_cart is not None:
            self.shopping_cart = shopping_cart

        # Disable ripple effect
        self.ripple_scale = 0

        # Mail addresses
        self.alternative_purchaser_list: List[PurchaserItem] = []

        self.purchaser_list_dialog = None

        # Create dialog if it wasn't created before.
        if price is not None and shopping_cart is not None:
           App.get_running_app().loop.call_soon_threadsafe(self.load_dialog_screen)

    def on_add_product(self):
        # Update the count on the UI
        self.ids.count.text = str(int(self.ids.count.text) + 1)

        # Create purchase object
        purchase = Purchase(App.get_running_app().active_user, self.text, 1)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

    def on_remove_product(self):
        if int(self.ids.count.text) > 0:
            self.ids.count.text = str(int(self.ids.count.text) - 1)

            # Create purchase object
            purchase = Purchase(App.get_running_app().active_user, self.text, 1)

            # Remove product from the shopping cart
            self.shopping_cart.remove_from_cart(purchase)

    #
    # open when trying to add a purchase for someone else
    #
    def on_select_purchaser(self):
        # Open the dialog to display the shopping cart
        self.purchaser_list_dialog.open()

    def on_ok(self, dt):
        if self.purchaser_list_dialog:
            self.purchaser_list_dialog.dismiss()

    def clear_item(self):
        # Clear the count of the item
        self.ids.count.text = "0"

        # Clear the count of the items for other users (if the dialog was opened).
        if self.purchaser_list_dialog is not None:
            for purchaser_item in self.purchaser_list_dialog.items:
                purchaser_item.ids.count.text = "0"

    def load_dialog_screen(self):
        start_time = time.time()

        for user_name, user_email in sorted(App.get_running_app().user_mapping.items()):
            self.alternative_purchaser_list.append(
                PurchaserItem(text=user_name, product_name=self.text, shoppingcart=self.shopping_cart,
                              secondary_text=" ", secondary_theme_text_color="Custom",
                              secondary_text_color=[0.509, 0.509, 0.509, 1])
            )

        print(f"Added user to dialog screen in {time.time() - start_time} seconds")

        self.purchaser_list_dialog = MDDialog(
            type="confirmation",
            height="440px",
            width="700px",
            items=self.alternative_purchaser_list,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=self.on_ok
                ),
            ],
        )

        print(f"Loaded dialog screen of item-ux view in {time.time() - start_time} seconds")

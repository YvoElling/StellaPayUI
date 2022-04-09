import time
from typing import List

from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem

from ds.Purchase import Purchase
from ds.ShoppingCart import ShoppingCart
from ux.PurchaserItem import PurchaserItem
from ux.SelectPurchaserDialog import SelectPurchaserDialog

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    # Dialog that opens when you want to select a different purchaser
    purchaser_list_dialog = None
    purchaser_list_children = []


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
        if self.purchaser_list_dialog is None:
            # If the dialog has not been loaded before, make sure to load it for the first time.
            self.load_dialog_screen()
        else:
            # It's already been built, so only refresh the contents
            self.refresh_dialog_count()

        # Open the dialog to display the users you may select.
        self.purchaser_list_dialog.open()

    def on_ok(self, dt):
        # Called when the dialog is opened
        if self.purchaser_list_dialog:
            self.purchaser_list_dialog.dismiss()

    def clear_item(self):
        # Clear the count of the item
        self.ids.count.text = "0"

        # Clear the count of the items for other users (if the dialog was opened).
        if ItemListUX.purchaser_list_dialog is not None:
            for purchaser_item in ItemListUX.purchaser_list_dialog.items:
                purchaser_item.ids.count.text = "0"

    @mainthread
    def load_dialog_screen(self):
        start_time = time.time()

        if ItemListUX.purchaser_list_dialog is None:

            if len(ItemListUX.purchaser_list_children) < 1:
                for user_name, user_email in App.get_running_app().user_mapping.items():
                    ItemListUX.purchaser_list_children.append(
                        PurchaserItem(text=user_name, secondary_text=" ", secondary_theme_text_color="Custom",
                                      secondary_text_color=[0.509, 0.509, 0.509, 1])
                    )

            Logger.debug(f"Creating purchasing items took {time.time() - start_time} seconds")

            ItemListUX.purchaser_list_dialog = SelectPurchaserDialog(
                shopping_cart=self.shopping_cart,
                type="confirmation",
                title="Selecteer hoeveelheid voor anderen",
                height="500px",
                width="720px",
                items=ItemListUX.purchaser_list_children,
                buttons=[
                    MDRaisedButton(
                        text="Selecteer",
                        on_release=self.on_ok
                    ),
                ],
            )

            Logger.debug(f"Creating additional itemlistux took {time.time() - start_time} seconds")

            # Make sure to provide the purchaser item class with a reference to the dialog we will open
            PurchaserItem.purchaser_dialog = ItemListUX.purchaser_list_dialog

            Logger.debug(f"Loaded dialog screen of item-ux view in {time.time() - start_time} seconds")

    # Because we are using a single dialog, we need to refresh its contents when we open and close it.
    # This method does exactly that.
    def refresh_dialog_count(self):
        # Make sure to update for which product the dialog is being opened
        SelectPurchaserDialog.selected_product = self.text

        # Show correct counts of items for this dialog screen
        for purchaser_item in ItemListUX.purchaser_list_dialog.items:
            # Loop over every name in the dialog
            is_in_shopping_cart = False

            # Check if we find a matching purchase in the shoppping cart
            for product in self.shopping_cart.get_shopping_cart():
                if product.product_name == self.text and product.purchaser_name == purchaser_item.get_purchaser_name():
                    # If we find a match, set the count to the current amount in the shopping cart
                    purchaser_item.set_item_count(product.amount)
                    is_in_shopping_cart = True

            # If we did not find a match, set the current count to zero.
            if not is_in_shopping_cart:
                purchaser_item.set_item_count(0)

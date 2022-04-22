from typing import Optional, Callable

from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem

from ux.SelectOtherPurchaserDialog import SelectOtherPurchaserDialog

Builder.load_file('kvs/ProductListItem.kv')


class ProductListItem(TwoLineAvatarIconListItem):
    # Dialog that opens when you want to select a different purchaser
    purchaser_list_dialog: SelectOtherPurchaserDialog = None

    # Callbacks that are called whenever a product is added or removed by the user
    on_product_added_callback: Optional[Callable[[str, str, int], None]] = None
    on_product_removed_callback: Optional[Callable[[str, str, int], None]] = None

    # Callback that is called whenever we want to set the exact amount of a product
    on_product_set_callback: Optional[Callable[[str, str, int], None]] = None

    product_screen: Optional["ProductScreen"] = None

    def __init__(self, price: Optional[str], **kwargs):
        super(ProductListItem, self).__init__(**kwargs)

        # When the price is none of the shopping cart is none, this is a special edge case where we don't want the user to see the buttons
        if price is None:
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

        # Disable ripple effect
        self.ripple_scale = 0

        # Create dialog if it wasn't created before.
        if price is not None:
            App.get_running_app().loop.call_soon_threadsafe(self.load_dialog_screen)

    def on_add_product(self):
        # Let caller know that we want to add an item to the shopping cart
        ProductListItem.on_product_added_callback(App.get_running_app().active_user, self.text, 1)

    def on_remove_product(self):
        if int(self.ids.count.text) > 0:
            # Let caller know that we want to remove an item from the shopping cart
            ProductListItem.on_product_removed_callback(App.get_running_app().active_user, self.text, 1)

    #
    # Called when the user wants to select a purchaser for a product
    #
    def on_select_purchaser(self):
        if self.purchaser_list_dialog is None:
            # If the dialog has not been loaded before, make sure to load it for the first time.
            self.load_dialog_screen()
        else:
            # It's already been built, so only refresh the contents of the dialog
            self.purchaser_list_dialog.reset_dialog_state()

        # Set the title of the dialog
        self.purchaser_list_dialog.title = f"Koop '{self.text}' als een andere gebruiker:"

        # Open the dialog to display the users you may select.
        self.purchaser_list_dialog.show_dialog(product=self.text)

    def on_ok(self, dt):
        # Called when the dialog is opened
        if self.purchaser_list_dialog:
            self.purchaser_list_dialog.dismiss()

    def clear_item(self):
        # Clear the count of the item
        self.ids.count.text = "0"

    @mainthread
    def load_dialog_screen(self):
        # Create the dialog for selecting a different purchaser (if it didn't exist yet).
        if ProductListItem.purchaser_list_dialog is None:
            ProductListItem.purchaser_list_dialog = SelectOtherPurchaserDialog()
            ProductListItem.purchaser_list_dialog.bind(
                selected_user=lambda _, selected_user: ProductListItem.selected_other_purchaser(selected_user,
                                                                                                ProductListItem.purchaser_list_dialog.selected_amount,
                                                                                                ProductListItem.purchaser_list_dialog.product))

    @classmethod
    # Fired when the user selects a purchaser
    def selected_other_purchaser(cls, selected_user_name: Optional[str], amount: int, selected_product: Optional[str]):
        # Close the dialog screen
        ProductListItem.purchaser_list_dialog.close_dialog()

        # Check if a user was actually selected
        if selected_user_name is None:
            Logger.debug("StellaPayUI: No user selected!")
            return

        # Let product screen know that we selected a product
        ProductListItem.on_product_set_callback(selected_user_name, selected_product, amount)

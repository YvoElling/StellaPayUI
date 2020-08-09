from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem

from ds.Purchase import Purchase
from ux.PurchaserItem import PurchaserItem

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    def __init__(self, price, shopping_cart, **kwargs):
        super(ItemListUX, self).__init__(**kwargs)
        self.ids.price.text = price
        self.shopping_cart = shopping_cart

        # Disable ripple effect
        self.ripple_scale = 0

        # Mail addresses
        self.mail_addresses = []

        # Purchaser list dialog
        self.purchaser_list_dialog = None

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
        if not self.mail_addresses:

            for user_name, user_email in sorted(App.get_running_app().user_mapping.items()):

                # We do not want to show the active user in this list.
                if user_name == App.get_running_app().active_user:
                    continue

                self.mail_addresses.append(PurchaserItem(text=user_name,
                                                         product_name=self.text,
                                                         shoppingcart=self.shopping_cart,
                                                         secondary_text=" ",
                                                         secondary_theme_text_color="Custom",
                                                         secondary_text_color=[0.509, 0.509, 0.509, 1])
                                           )

        if not self.purchaser_list_dialog:
            self.purchaser_list_dialog = MDDialog(
                type="confirmation",
                height="440px",
                width="700px",
                items=self.mail_addresses,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=self.on_ok
                    ),
                ],
            )
        # Open the dialog to display the shopping cart
        self.purchaser_list_dialog.open()

    def on_ok(self, dt):
        if self.purchaser_list_dialog:
            self.purchaser_list_dialog.dismiss()

    # Store purchaser
    def on_set_mail(self, item):
        # Create purchase object
        purchase = Purchase(item.text, self.text, 1)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

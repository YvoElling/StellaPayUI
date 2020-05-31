from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarIconListItem
import requests

from ds.Purchase import Purchase
from ux.PurchaserItem import PurchaserItem

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    def __init__(self, user_mail, price, shoppingcart, cookies, **kwargs):
        super(ItemListUX, self).__init__(**kwargs)
        self.ids.price.text = price
        self.user_mail = user_mail
        self.shopping_cart = shoppingcart
        self.requests_cookies = cookies

        # Mail addresses
        self.mail_addresses = []

        # Purchaser list dialog
        self.purchaser_list_dialog = None

    def on_add_product(self):
        # Update the count on the UI
        self.ids.count.text = str(int(self.ids.count.text) + 1)

        # Create purchase object
        purchase = Purchase(self.user_mail, self.text, 1)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

    def on_remove_product(self):
        if int(self.ids.count.text) > 0:
            self.ids.count.text = str(int(self.ids.count.text) - 1)

            # Create purchase object
            purchase = Purchase(self.user_mail, self.text, 1)

            # Remove product from the shopping cart
            self.shopping_cart.remove_from_cart(purchase)

    #
    # open when trying to add a purchase for someone else
    #
    def on_select_purchaser(self):
        if not self.mail_addresses:
            # Query all
            user_data = self.requests_cookies.get("http://staartvin.com:8181/users")

            if user_data.ok:
                # convert to json
                user_json = user_data.json()

                # append json to list and sort the list
                for user in user_json:
                    # store all emails adressed in the sheet_menu
                    user_mail = user['email']
                    if user_mail != self.user_mail:
                        self.mail_addresses.append(PurchaserItem(text=user_mail,
                                                                 product_name=self.text,
                                                                 user_mail=user['name'],
                                                                 shoppingcart=self.shopping_cart,
                                                                 tertiary_text=" ",
                                                                 tertiary_theme_text_color="Custom",
                                                                 tertiary_text_color=[0.509, 0.509, 0.509, 1])
                                                   )
            else:
                print("Error: addresses could not be fetched from server")
                exit(9)
        if not self.purchaser_list_dialog:
            self.purchaser_list_dialog = MDDialog(
                type="confirmation",
                height="440px",
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

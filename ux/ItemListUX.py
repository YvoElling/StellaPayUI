from kivy.lang import Builder
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.list import TwoLineAvatarIconListItem, IRightBodyTouch
import requests

from ds.Purchase import Purchase

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    def __init__(self, user_mail, price, shoppingcart, **kwargs):
        super(ItemListUX, self).__init__(**kwargs)
        self.ids.price.text = price
        self.user_mail = user_mail
        self.shopping_cart = shoppingcart

        # Mail addresses
        self.mail_addresses = []

    def on_add_product(self):
        # Update the count on the UI
        self.ids.count.text = str(int(self.ids.count.text) + 1)

        # Create purchase object
        mail = self.user_mail
        product_name = self.text
        count = 1
        purchase = Purchase(mail, product_name, count)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

    def on_remove_product(self):
        if int(self.ids.count.text) > 0:
            self.ids.count.text = str(int(self.ids.count.text) - 1)

            # Create purchase object
            mail = self.user_mail
            product_name = self.text
            count = 1
            purchase = Purchase(mail, product_name, count)

            # Remove product from the shopping cart
            self.shopping_cart.remove_from_cart(purchase)

    #
    # open when trying to add a purchase for someone else
    #
    def on_select_purchaser(self):
        if not self.mail_addresses:
            # Query all
            user_data = requests.get("http://staartvin.com:8181/users")

            if user_data.ok:
                # convert to json
                user_json = user_data.json()

                # append json to list and sort the list
                for user in user_json:
                    # store all emails adressed in the sheet_menu
                    self.mail_addresses.append(user["email"])
            else:
                print("Error: addresses could not be fetched from server")
                exit(9)

            self.mail_addresses.sort()

        # Add items to the bottom list
        bottom_sheet_menu = MDListBottomSheet(height="200dp")

        for user in self.mail_addresses:
            # store all emails addresses in the sheet_menu
            bottom_sheet_menu.add_item(user, self.on_set_mail)
        # open the bottom sheet menu
        bottom_sheet_menu.open()

    # Store purchaser
    def on_set_mail(self, item):
        mail = item.text
        product_name = self.text
        count = 1
        purchase = Purchase(mail, product_name, count)

        # Add purchase to shopping cart
        self.shopping_cart.add_to_cart(purchase)

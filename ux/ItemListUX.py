from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem, IRightBodyTouch

from ds.Purchase import Purchase

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    def __init__(self, user_mail, price, shoppingcart, **kwargs):
        super(ItemListUX, self).__init__(**kwargs)
        self.ids.price.text = price
        self.user_mail = user_mail
        self.shopping_cart = shoppingcart

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

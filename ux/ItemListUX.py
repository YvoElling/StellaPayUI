from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem

Builder.load_file('kvs/ItemListUX.kv')


class ItemListUX(TwoLineAvatarIconListItem):
    def __init__(self, price, shoppingcart, **kwargs):
        super(ItemListUX, self).__init__(**kwargs)
        self.ids.price.text = price
        self.shopping_cart = shoppingcart

    def __on_add_product(self):
        self.ids.count = str(int(self.ids.count) + 1)

from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem

Builder.load_file('kvs/ShoppingCartItem.kv')


class ShoppingCartItem(TwoLineAvatarIconListItem):

    def __init__(self, purchase, **kwargs):
        super(ShoppingCartItem, self).__init__(**kwargs)

        self.ids.amount.text = str(purchase.amount)
        self.ids.buyer.text = purchase.email




from kivy.lang import Builder
from kivymd.uix.list import OneLineAvatarIconListItem

from ds.Purchase import Purchase

Builder.load_file('kvs/ShoppingCartItem.kv')


class ShoppingCartItem(OneLineAvatarIconListItem):

    def __init__(self, purchase: Purchase, **kwargs):
        super(ShoppingCartItem, self).__init__(**kwargs)

        self.ids.amount.text = str(purchase.amount)
        self.ids.buyer.text = purchase.purchaser_name

        # Disable ripple effect
        self.ripple_scale = 0

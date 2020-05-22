from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem

Builder.load_file('kvs/PurchaserItem.kv')


class PurchaserItem(TwoLineAvatarIconListItem):

    def __init__(self, **kwargs):
        super(PurchaserItem, self).__init__(**kwargs)

    def on_add_product(self):
        pass

    def on_remove_product(self):
        pass


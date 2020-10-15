import time

from kivy.lang import Builder
from kivymd.uix.list import OneLineAvatarIconListItem

Builder.load_file('kvs/PurchaserItem.kv')


class PurchaserItem(OneLineAvatarIconListItem):
    purchaser_dialog: "SelectPurchaserDialog" = None

    # Set local member variables and forwards **kwargs to super class
    def __init__(self, **kwargs):
        start_time = time.time()
        super(PurchaserItem, self).__init__(**kwargs)

        # Disable ripple effect
        self.ripple_scale = 0
        print(f"Init function of purchaseritem done in {time.time() - start_time} seconds")

    # Adds product to the shopping cart.
    def on_add_product(self):
        # Update count
        self.ids.count.text = str(int(self.ids.count.text) + 1)

        self.purchaser_dialog.on_add_product(self.get_purchaser_name())

    # Removes item from the shopping cart
    def on_remove_product(self):
        # Items can only be removed from the shopping cart when count > 0
        if int(self.ids.count.text) > 0:
            self.ids.count.text = str(int(self.ids.count.text) - 1)

            self.purchaser_dialog.on_remove_product(self.get_purchaser_name())

    def set_item_count(self, count: int):
        self.ids.count.text = str(count)

    def get_item_count(self) -> int:
        return int(self.ids.count.text)

    def get_purchaser_name(self) -> str:
        return self.text

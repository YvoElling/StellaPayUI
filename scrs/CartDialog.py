from kivymd.material_resources import DEVICE_TYPE
from kivymd.uix.card import MDSeparator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import BaseListItem


class CartDialog(MDDialog):
    def __init__(self, list_content, **kwargs):
        super().__init__(**kwargs)
        self.ids.title.theme_text_color = "Custom"
        self.ids.title.text_color = (1, 1, 1, 1)

        self.ids.spacer_top_box.add_widget(MDSeparator())
        self.ids.spacer_bottom_box.add_widget(MDSeparator())

        height = 0
        for item in list_content:
            if issubclass(item.__class__, BaseListItem):
                height += item.height  # calculate height contents
                self.edit_padding_for_item(item)
                self.ids.box_items.add_widget(item)

        self.ids.scroll.height = height

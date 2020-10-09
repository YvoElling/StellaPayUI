from typing import Callable

from kivy.lang import Builder
from kivymd.uix.list import OneLineIconListItem

Builder.load_file('kvs/SelectUserItem.kv')


class SelectUserItem(OneLineIconListItem):

    def __init__(self, user_email: str, callback: Callable = None, **kwargs):
        # Store user email and callback
        self.user_email = user_email
        self.callback = callback

        super(SelectUserItem, self).__init__(**kwargs)

        # When we click the username, run the callback
        self.bind(on_press=self.callback)

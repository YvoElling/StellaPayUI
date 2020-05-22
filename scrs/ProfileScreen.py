from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition


class ProfileScreen(Screen):

    Builder.load_file('kvs/ProfileScreen.kv')

    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)

    # Called when the screen is loaded:
    # - for retrieving user name
    def on_enter(self, *args):
        self.ids.username.text = self.manager.get_screen("DefaultScreen").user_name

    # Return to the product page
    def on_back(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ProductScreen'

    # Clear name on leave
    def on_leave(self, *args):
        self.ids.username.text = ""

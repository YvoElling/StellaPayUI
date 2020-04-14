from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


class RegisterUIDScreen(Screen):

    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/RegisterUIDScreen.kv')

        # call to user with arguments
        super(RegisterUIDScreen, self).__init__(**kwargs)


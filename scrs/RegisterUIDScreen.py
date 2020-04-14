from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


class RegisterUIDScreen(Screen):

    def __init__(self, **kwargs):
        super(RegisterUIDScreen, self).__init__(**kwargs)

        # Load KV file for this screen
        Builder.load_file('kvs/RegisterUIDScreen.kv')

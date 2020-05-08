from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/CreditsScreen.kv')

        # call to user with arguments
        super(CreditsScreen, self).__init__(**kwargs)

    def on_stop(self):
        self.manager.current = 'DefaultScreen'

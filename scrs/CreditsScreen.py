from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, CardTransition


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/CreditsScreen.kv')

        # call to user with arguments
        super(CreditsScreen, self).__init__(**kwargs)

    #
    # used to return to the welcome pages. Callback function from stop button
    #
    def on_stop(self):
        self.manager.transition = CardTransition(direction="up", mode="push")
        self.manager.current = 'DefaultScreen'

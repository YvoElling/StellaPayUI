from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from utils.Screens import Screens


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/CreditsScreen.kv')

        # call to user with arguments
        super(CreditsScreen, self).__init__(**kwargs)

        # timeout variables
        self.timeout_event = None
        self.timeout_time = 45

    def on_leave(self, *args):
        self.timeout_event.cancel()

    def clicked_stop_button(self):
        self.on_timeout(0)

    #
    # calls upon entry of this screen
    #
    def on_enter(self, *args):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    #
    # Timeout callback function.
    #
    def on_timeout(self, dt):
        self.manager.current = Screens.DEFAULT_SCREEN.value

    #
    # when the screen is touched, reset the timer
    #
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.on_enter()

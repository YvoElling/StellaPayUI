from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from utils.Screens import Screens


class ProfileScreen(Screen):
    Builder.load_file('kvs/ProfileScreen.kv')

    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)

        # timeout variables
        self.timeout_event = None
        self.timeout_time = 45  # Seconds

    # Called when the screen is loaded:
    # - for retrieving user name
    def on_enter(self, *args):
        self.ids.username.text = App.get_running_app().active_user
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    # Return to the product page
    def on_back(self):
        self.manager.current = Screens.PRODUCT_SCREEN.value

    # Called when timer is timed out
    def on_timeout(self, dt):
        # Make sure to clean up product screen after going to profile screen
        self.manager.get_screen(Screens.PRODUCT_SCREEN.value).end_user_session()

        self.manager.current = Screens.DEFAULT_SCREEN.value

    # Reset timer when the screen is touched
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    # Clear time on leave
    def on_leave(self, *args):
        self.timeout_event.cancel()

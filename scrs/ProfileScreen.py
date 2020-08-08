from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


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
        self.ids.username.text = self.manager.get_screen(Screen.DEFAULT_SCREEN.name).user_name
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    # Return to the product page
    def on_back(self):
        self.manager.current = Screen.PRODUCT_SCREEN.name
        self.timeout_event.cancel()

    # Return to defaultScreen upon timeout
    def on_timeout(self, dt):
        self.manager.current = Screen.DEFAULT_SCREEN.name

    # Reset timer when the screen is touched
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    # Clear name on leave
    def on_leave(self, *args):
        self.ids.username.text = ""
        self.manager.get_screen("ProductScreen") \
            .load_data(self.manager.get_screen(Screen.DEFAULT_SCREEN.name).static_database)

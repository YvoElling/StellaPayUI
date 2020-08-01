from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivymd.uix.taptargetview import MDTapTargetView


class WelcomeScreen(Screen):

    def __init__(self, **kwargs):
        Builder.load_file('kvs/WelcomeScreen.kv')
        super(WelcomeScreen, self).__init__(**kwargs)

        # timeout variables
        self.timeout_event = None
        self.timeout_time = 30  # Seconds

        # connect tap-target-view
        self.tap_target_view = MDTapTargetView(
            widget=self.ids.info,
            title_text="Version Information",
            description_text="Release 01-08-20: Version 0.7\n",
            widget_position="right_bottom"
        )

    #
    # performed upon each screen entry
    #
    def on_enter(self, *args):
        # Set timer of duration @timeout_time
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    #
    # callback function on timeout
    #
    def on_timeout(self, dt):
        self.on_cancel()

    #
    # when the screen is touched, we restart the timer
    #
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.on_enter()

    #
    # Called when the stop button is pressed
    #
    def on_cancel(self):
        # If tap target view is open, close it
        if self.tap_target_view.state == "open":
            self.tap_target_view.stop()

        # Clean up the loaded products that are stored in the tabs
        self.manager.get_screen("ProductScreen").on_cleanup()
        # Switch back to the default screen to welcome a new user
        self.manager.current = 'DefaultScreen'

    #
    # Called when buy is pressed
    #
    def on_buy(self):
        self.timeout_event.cancel()
        self.manager.get_screen('ProductScreen').user_name = self.ids.label.text
        self.manager.current = 'ProductScreen'

    #
    # Opens the little information screen at the right bottom
    #
    def tap_target_start(self):
        if self.tap_target_view.state == "close":
            self.tap_target_view.start()
        else:
            self.tap_target_view.stop()

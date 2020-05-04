from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock
from kivy.lang import Builder


class WelcomeScreen(Screen):

    def __init__(self, **kwargs):
        Builder.load_file('kvs/WelcomeScreen.kv')
        super(WelcomeScreen, self).__init__(**kwargs)

        # Schedule a timeout in @timeout seconds upon start
        self.timeout = 25
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

    #
    # Called when the 'stop' button is pressed or timeout is induced
    #
    def on_timeout(self, dt):
        Clock.unschedule(self.timeout_event)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # Called when buy is pressed
    #
    #
    def on_buy(self):
        Clock.unschedule(self.timeout_event)
        self.manager.get_screen('ProductScreen').user_name = self.ids.label.text
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ProductScreen'

    #
    # Reset timer when the screen is pressed
    #
    def on_touch_up(self, touch):
        Clock.unschedule(self.timeout_event)
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock


class WelcomeScreen(Screen):

    # timeout time in seconds
    timeout = 15

    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)

        # Schedule a timeout in @timeout seconds upon start
        self.timeout_event = Clock.schedule_once(self.on_cancel, self.timeout)

    #
    # Called when the 'stop' button is pressed
    #
    def on_cancel(self, dt):
        Clock.unschedule(self.timeout_event)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # Called when buy is pressed
    #
    #
    def on_buy(self):
        Clock.unschedule(self.timeout_event)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ProductScreen'

    #
    # Reset timer when the screen is pressed
    #
    def on_touch_up(self, touch):
        Clock.unschedule(self.timeout_event)
        self.timeout_event = Clock.schedule_once(self.on_cancel, self.timeout)

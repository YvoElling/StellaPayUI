from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, CardTransition


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/CreditsScreen.kv')

        # call to user with arguments
        super(CreditsScreen, self).__init__(**kwargs)

        # define time_out event
        self.timeout_event = None

    #
    # used to return to the welcome pages. Callback function from stop button
    #
    def on_stop(self):
        self.manager.transition = CardTransition(direction="up", mode="push")
        self.manager.current = 'DefaultScreen'

    #
    # Called on time_out, forces a @on_stop() function call
    #
    def on_timeout(self, dt):
        self.on_stop()

    #
    # Upon entering the creditsScreen, start the time-out counter
    #
    def on_enter(self, *args):
        timeout_time = 30  # seconds
        self.timeout_event = Clock.schedule_once(self.on_timeout, timeout_time)

    #
    #
    #
    def on_touch_up(self, touch):
        timeout_time = 30 # seconds
        Clock.unschedule(self.timeout_event)
        self.timeout_event = Clock.schedule_once(self.on_timeout, timeout_time)

    #
    # Upon leaving this screen, stop the timeout function.
    #
    def on_leave(self, *args):
        Clock.unschedule(self.timeout_event)

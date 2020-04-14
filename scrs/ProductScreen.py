from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock
from kivy.lang import Builder


class ProductScreen(Screen):
    # Timer timeout in @timeout seconds
    timeout = 30

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Schedule on_cancel() event in @timeout seconds
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

    #
    # Called when the 'stop' button is pressed
    #
    def on_timeout(self, dt):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # reset timeout timer on screen pressed
    #
    def on_touch_up(self, touch):
        Clock.unschedule(self.timeout_event)
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

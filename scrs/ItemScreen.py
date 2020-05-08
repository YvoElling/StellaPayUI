from kivy.clock import Clock
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


class ItemScreen(Screen):

    def __init__(self, **kwargs):
        # Load kv
        Builder.load_file('kvs/ItemScreen.kv')

        # Call to super
        super(ItemScreen, self).__init__(**kwargs)
        self.timeout = None
        self.timeout_event = None

        # Get items from API
        cat = self.ids.title.text
        items = ['a', 'b', 'c'] #INSERT API CALL here

        for item in items:
            # Create rectangle object and set properties
            item_panel = Rectangle(text=item)

            # Set item panel properties

            # Add item panel to the boxLayout

    def on_return(self):
        Clock.unschedule(self.timeout_event)
        self.manager.current = 'ProductScreen'

    def on_touch_up(self, touch):
        Clock.unschedule(self.timeout_event)
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

    def on_timeout(self, dt):
        self.manager.current = 'DefaultScreen'

    def on_enter(self, *args):
        # Schedule timeout
        self.timeout = 30
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

    def on_profile_screen(self):
        self.manager.current = 'ProfileScreen'

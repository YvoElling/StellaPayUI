from kivy.uix.screenmanager import Screen, SlideTransition
from ux.cat_item import CategoryItem
from kivy.clock import Clock
from kivy.lang import Builder


class ProductScreen(Screen):

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Schedule on_cancel() event in @timeout seconds
        self.timeout = 30
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

        # add categories to productScreen
        self.add_categories()

    def add_categories(self):
        ci_drinks = CategoryItem('img/STEverysmall.png', "Drinken", self.drinks_callback)
        self.children[0].children[0].add_widget(ci_drinks)


    def drinks_callback(self):
        print("here!")
        pass

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

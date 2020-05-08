from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, SlideTransition, NoTransition
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.tab import MDTabsBase


class ProductScreen(Screen):
    user_name = None

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Schedule on_cancel() event in @timeout seconds
        self.timeout = 30
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

        # Configure tabs
        self.ids.android_tabs.add_widget(Tab(text=f"Eten"))
        self.ids.android_tabs.add_widget(Tab(text=f"Drinken"))
        self.ids.android_tabs.add_widget(Tab(text=f"Alcohol"))

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

    #
    # when a category is selected, retrieve the items in that category
    #
    def on_cat_selected(self, cat):
        Clock.unschedule(self.timeout_event)
        self.manager.transition = NoTransition()
        self.manager.get_screen('ItemScreen').ids.title.text = cat
        self.manager.current = 'ItemScreen'

    #
    # move to profile screen
    #
    def on_profile_screen(self):
        Clock.unschedule(self.timeout_event)
        self.manager.current = 'ProfileScreen'

    #
    # on switch tab
    #
    def on_tab_switch(self, *args):
        pass


class Tab(FloatLayout, MDTabsBase):
    pass

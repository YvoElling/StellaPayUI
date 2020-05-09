from kivy.uix.screenmanager import Screen, SlideTransition, NoTransition
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from scrs.TabDisplay import TabDisplay


class ProductScreen(Screen):
    user_name = None

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Schedule on_cancel() event in @timeout seconds
        self.timeout = 45
        self.timeout_event = None
        self.direct_confirm = None
        self.shoppingcart = None

        # Add tabs to the tab bar
        self.ids.android_tabs.add_widget(TabDisplay(text=f"Eten"))
        self.ids.android_tabs.add_widget(TabDisplay(text=f"Drinken"))
        self.ids.android_tabs.add_widget(TabDisplay(text=f"Alcohol"))

    #
    # upon entering the screen, set the timeout
    #
    def on_enter(self, *args):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

    #
    # upon leaving the screen, cancel the timeout event
    #
    def on_leave(self, *args):
        Clock.unschedule(self.timeout_event)

    #
    # Called when the 'stop' button is pressed
    #
    def on_timeout(self, dt):
        if self.direct_confirm:
            self.direct_confirm.dismiss()
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
    # callback function for when tab is switched
    #
    def on_tab_switch(self, *args):
        pass

    #
    # open confirmation dialog
    #
    def open_confirmation(self):
        if not self.direct_confirm:
            self.direct_confirm = MDDialog(
                text="Voeg deze aankopen aan mijn account toe",
                buttons=[
                    MDFlatButton(
                        text="TERUG",
                        on_release=self.on_return_direct_confirm

                    ),
                    MDRaisedButton(
                        text="BEVESTIG",
                        md_bg_color=[0.933, 0.203, 0.125, 1]
                    ),
                ],
            )
        self.direct_confirm.open()

    def show_shoppingcart(self):
        if not self.shoppingcart:
            self.shoppingcart = MDDialog(
                title="Winkelmandje",
                type="confirmation",
                # items=[
                #     Item(text="Callisto"),
                #
                # ],
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.on_return_shoppingcart
                    ),
                    MDFlatButton(
                        text="OK",
                        on_release=self.on_return_direct_confirm
                    ),
                ],
            )
        self.shoppingcart.open()

    #
    # Close dialog when TERUG is pressed
    #
    def on_return_shoppingcart(self, dt):
        self.shoppingcart.dismiss()

    #
    # Close dialog when TERUG is pressed
    #
    def on_return_direct_confirm(self, dt):
        self.direct_confirm.dismiss()

    #
    # Confirm addition
    #
    def on_confirm(self, dt):
        # Perform API purchase confirmation here
        pass

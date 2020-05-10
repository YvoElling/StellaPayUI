from kivy.uix.screenmanager import Screen, SlideTransition, NoTransition
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem

from ds import Product
from ds.ShoppingCart import ShoppingCart
from scrs.TabDisplay import TabDisplay
import requests

class ProductScreen(Screen):
    # Store user_name
    user_name = None

    # Store items per category
    local_items = {}

    # api link
    get_cat_api_url = "http://staartvin.com:8181/products/"

    # shopping cart
    shoppping_cart = ShoppingCart()

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Class level variables
        self.timeout = 45
        self.timeout_event = None
        self.direct_confirm = None
        self.shoppingcart = None

        # Add tabs to the tab bar
        categories = ["Eten", "Drinken", "Alcohol"]
        for cat in categories:
            self.ids.android_tabs.add_widget(TabDisplay(text=cat))
            self.local_items[cat] = []

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
    # move to profile screen
    #
    def on_profile_screen(self):
        Clock.unschedule(self.timeout_event)
        self.manager.current = 'ProfileScreen'

    #
    # callback function for when tab is switched
    #
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        # consult local_items first, if empty, request items from server
        if not self.local_items[tab_text]:
            # Request products from category tab_text
            request = self.get_cat_api_url + tab_text
            response = requests.get(request)

            # Evaluate server response
            if response.ok:
                # convert response to json
                products_json = response.json()

                # Create a product object for all
                for product in products_json:
                    # Only add the product to the list if the product must be shown
                    if product['shown']:
                        p = Product.create_from_json(product)
                        self.local_items[tab_text].append(p)

        # For all items in the local_items list, add them to the container and display them
        for product in self.local_items[tab_text]:
            self.ids.container.add_widget(OneLineListItem(text=product.get_name()))

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

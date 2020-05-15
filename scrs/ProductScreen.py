from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart
from scrs.TabDisplay import TabDisplay
from ux.ItemListUX import ItemListUX
import requests

from ux.ShoppingCartItem import ShoppingCartItem


class ProductScreen(Screen):
    # Store items per category, these are stored locally to reduce the amount of queries required
    local_items = {}
    # Store tab objects, these are later used to add the products
    tabs = []

    # API Links
    get_cat_api_url = "http://staartvin.com:8181/products/"
    get_all_cat_api = "http://staartvin.com:8181/categories"
    confirm_api = "http://staartvin.com:8181/transactions/create"

    # shopping cart
    shopping_cart = ShoppingCart()

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Class level variables
        self.timeout = 120
        self.timeout_event = None
        self.direct_confirm = None
        # Shopping_cart dialog screen object
        self.shopping_cart_dialog = None

        # Get all categories names
        response = requests.get(url=self.get_all_cat_api)

        # Check status response
        if response.ok:
            categories = response.json()

            # add all tabs to the tabbar
            for cat in categories:
                # Create tab display
                tab = TabDisplay(text=cat['name'])
                self.tabs.append(tab)
                self.ids.android_tabs.add_widget(tab)
                self.local_items[cat['name']] = []

                # Request products from category tab_text
                request = self.get_cat_api_url + cat['name']
                response = requests.get(request)

                # Evaluate server response
                if response.ok:
                    # convert response to json
                    products_json = response.json()

                    # Create a product object for all
                    for product in products_json:
                        # Only add the product to the list if the product must be shown
                        if product['shown']:
                            p = Product().create_from_json(product)
                            self.local_items[cat['name']].append(p)
                else:
                    # Error in retrieving products from server
                    print("Products could not be retried: " + response)
                    exit(7)

        else:
            # Error
            print("Categories could not be retrieved: " + response)
            exit(6)

    #
    # upon entering the screen, set the timeout
    #
    def on_enter(self, *args):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

        # For all items in the local_items list, add them to the container and display them
        for tab in self.tabs:
            for product in self.local_items[tab.text]:
                tab.ids.container.add_widget(ItemListUX(text=product.get_name(),
                                                        user_mail=self.manager.get_screen("DefaultScreen").user_mail,
                                                        price="€" + product.get_price(),
                                                        shoppingcart=self.shopping_cart,
                                                        secondary_text="Fun fact about " + product.get_name(),
                                                        secondary_theme_text_color="Custom",
                                                        secondary_text_color=[0.509, 0.509, 0.509, 1]))

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
                        on_release=self.on_confirm,
                        md_bg_color=[0.933, 0.203, 0.125, 1]
                    ),
                ],
            )
        self.direct_confirm.open()

    #
    # opens shoppingcart display
    #
    def show_shoppingcart(self):
        # Create an empty list that will contain all purchases
        shopping_cart_items = []

        # Retrieve all items from shopping cart and store in local shopping cart list
        for purchase in self.shopping_cart.get_shopping_cart():
            item = ShoppingCartItem(purchase=purchase, secondary_text=purchase.product_name)
            shopping_cart_items.append(item)

        # If there are items in the shopping cart, display them
        if shopping_cart_items:
            self.shopping_cart_dialog = MDDialog(
                text="Winkelmandje",
                type="confirmation",
                items=shopping_cart_items,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.on_return_shoppingcart
                    ),
                    MDFlatButton(
                        text="OK",
                        on_release=self.on_return_shoppingcart
                    ),
                ],
            )
            # Open the dialog to display the shopping cart
            self.shopping_cart_dialog.open()

    #
    # Close dialog when TERUG is pressed
    #
    def on_return_shoppingcart(self, dt):
        self.shopping_cart_dialog.dismiss()

    #
    # Close dialog when TERUG is pressed
    #
    def on_return_direct_confirm(self, dt):
        self.shopping_cart_items.clear()
        self.direct_confirm.dismiss()

    #
    # Confirms a payment
    #
    def on_confirm(self, dt):
        # Serialize the shopping cart
        json_cart = self.shopping_cart.to_json()

        # use a POST-request to forward the shopping cart
        response = requests.post(self.confirm_api, json=json_cart)

        if response.ok:
            # Clear the offline storage of the items per category
            for cat in self.local_items:
                self.local_items[cat] = []

            # Clear the shopping cart
            self.shopping_cart.emtpy_cart()

            # Close the dialgo
            self.direct_confirm.dismiss()

            # Return to the default screen for a new user to log in
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = "DefaultScreen"

        else:
            print("Payment could not be made: error: " + response.content)
            exit(7)
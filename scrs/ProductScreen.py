import os
from asyncio import AbstractEventLoop
from typing import Dict, List

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from ds.Product import Product
from ds.ShoppingCart import ShoppingCart
from scrs.TabDisplay import TabDisplay
from utils.Connections import BackendURLs
from utils.Screens import Screens
from ux.ItemListUX import ItemListUX
from ux.ShoppingCartItem import ShoppingCartItem


class ProductScreen(Screen):
    # Store items per category, these are stored locally to reduce the amount of queries required
    products_per_category: Dict[str, List[Product]] = {}
    # Store tab objects, these are later used to add the products
    tabs = []

    product_items_per_category: Dict[str, List[ItemListUX]] = {}

    # shopping cart
    shopping_cart = ShoppingCart()

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Class level variables
        self.direct_confirm = None
        # Shopping_cart dialog screen object
        self.shopping_cart_dialog = None
        self.session = App.get_running_app().session

        # Timeout variables
        self.timeout_event = None
        self.timeout_time = 75

        self.event_loop: AbstractEventLoop = App.get_running_app().loop

    # Start timeout counter
    def on_start_timeout(self):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    #
    # when the screen is touched, reset the timeout counter
    #
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.on_start_timeout()

    # Load tabs (if they are not loaded yet) and load product information afterwards
    def load_category_data(self):

        if len(self.tabs) > 0:
            Logger.debug("Don't load tabs as we already have that information.")

            # Load product items (because we still need to reload them)
            self.load_products()

            return

        # Get all categories names
        response = self.session.get(url=BackendURLs.GET_CATEGORIES.value)

        Logger.debug("Loading product categories")

        # Check status response
        if response.ok:

            categories = response.json()

            Logger.debug(f"Retrieved {len(categories)} categories")

            # Load tab for each category
            for cat in categories:
                # Create tab display
                tab = TabDisplay(text=cat['name'])
                self.tabs.append(tab)
                self.ids.android_tabs.add_widget(tab)
                self.products_per_category[cat['name']] = []

                # Request products from category tab_text
                request = BackendURLs.GET_PRODUCTS.value + cat['name']
                response = self.session.get(request)

                # Evaluate server response
                if response.ok:
                    # convert response to json
                    products_json = response.json()

                    # Create a product object for all
                    for product in products_json:
                        # Only add the product to the list if the product must be shown
                        if product['shown']:
                            p = Product().create_from_json(product)
                            self.products_per_category[cat['name']].append(p)
                else:
                    # Error in retrieving products from server
                    Logger.critical("Products could not be retrieved: " + response.text)
                    os._exit(1)

        else:
            # Error
            Logger.critical("Categories could not be retrieved: " + response.text)
            os._exit(1)

        # Load product items
        self.load_products()


    #
    # upon entering the screen, set the timeout
    #
    def on_enter(self, *args):
        # Load category information and tabs
        self.event_loop.call_soon_threadsafe(self.load_category_data)

        # Initialize timeouts
        self.on_start_timeout()

    # Load product information and set up product view
    def load_products(self):
        Logger.debug(f"Setting up product view")

        if len(self.tabs[0].ids.container.children) > 0:
            Logger.debug("Don't load products view again as it's already there..")
            return

        for tab in self.tabs:
            for product in self.products_per_category[tab.text]:
                # Should update this to PREPARED STATEMENT instead of this, but it's fun facts, so what the heck
                # Get all fun facts for this product
                # database_conn.execute(
                #     "SELECT fun_fact FROM static_fun_facts WHERE product='" + product.get_name() + "'")
                #
                # # store all fun facts that were found for this product in a list.
                # fun_facts = database_conn.fetchall()

                product_description = "Zoveel facts gevonden als Stella's in 2012"
                # if fun_facts:
                #     # Select a random fun fact from the list
                #     pff = random.choice(fun_facts)
                #
                #     # Clean the fun fact by removing unnecessary tokens
                #     cff = str(pff).replace('(', '').replace(')', '').replace('\'', '').replace('\"', '')
                #     cff = cff[:-1]

                # Add item to the tab
                tab.ids.container.add_widget(ItemListUX(text=product.get_name(), secondary_text=product_description,
                                                        secondary_theme_text_color="Custom",
                                                        secondary_text_color=[0.509, 0.509, 0.509, 1],
                                                        price="€" + product.get_price(),
                                                        shopping_cart=self.shopping_cart))

            # Add last item to the products (for each category) that is empty. This improves readability.
            tab.ids.container.add_widget(ItemListUX(text="",
                                                    secondary_text="",
                                                    secondary_theme_text_color="Custom",
                                                    secondary_text_color=[0.509, 0.509, 0.509, 1],
                                                    price=None,
                                                    shopping_cart=None))

    #
    # timeout callback function
    #
    def on_timeout(self, dt):
        self.__end_process()

        # If the dialogs are instantiated, dismiss them before timeouts
        if self.direct_confirm:
            self.direct_confirm.dismiss()
        if self.shopping_cart_dialog:
            self.shopping_cart_dialog.dismiss()

        self.manager.current = Screens.DEFAULT_SCREEN.value

    #
    # upon leaving the screen, cancel the timeout event
    #
    def on_leave(self, *args):
        self.timeout_event.cancel()

    # Called when the user wants to leave this active session.
    def on_leave_product_screen_button(self):
        self.__end_process()
        self.manager.current = Screens.DEFAULT_SCREEN.value

    #
    # move to profile screen
    #
    def on_profile_screen(self):
        # Switch to profile screen
        self.manager.current = Screens.PROFILE_SCREEN.value

    #
    # callback function for when tab is switched
    #
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        pass

    #
    # Open payment confirmation dialog
    #
    def open_payment_confirmation(self):
        # Restart timeout counter
        self.timeout_event.cancel()
        self.on_start_timeout()

        shopping_cart_items = self.shopping_cart.get_shopping_cart()

        if shopping_cart_items:
            # Create direct_confirm dialog
            if not self.direct_confirm:
                self.direct_confirm = MDDialog(
                    title="",
                    text="Wil je deze artikelen afrekenen?",
                    buttons=[
                        MDFlatButton(
                            text="Nee",
                            on_release=self.on_cancel_payment

                        ),
                        MDRaisedButton(
                            text="Ja",
                            on_release=self.on_confirm_payment
                        ),
                    ]
                )
            self.direct_confirm.open()

    #
    # Open shopping cart dialog
    #
    def show_shopping_cart(self):
        # Reset timeout counter
        self.timeout_event.cancel()
        self.on_start_timeout()

        # Create an empty list that will contain all purchases
        shopping_cart_items = []

        # Retrieve all items from shopping cart and store in local shopping cart list
        for purchase in self.shopping_cart.get_shopping_cart():
            item = ShoppingCartItem(purchase=purchase,
                                    text=purchase.product_name,
                                    secondary_text="",
                                    secondary_theme_text_color="Custom",
                                    secondary_text_color=[0.509, 0.509, 0.509, 1])
            shopping_cart_items.append(item)

        # If there are items in the shopping cart, display them
        if shopping_cart_items:
            self.shopping_cart_dialog = MDDialog(
                type="confirmation",
                items=shopping_cart_items,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=self.on_close_shoppingcart
                    ),
                ],
            )

            # Open the dialog to display the shopping cart
            self.shopping_cart_dialog.open()

    #
    # When shopping cart needs to be closed
    #
    def on_close_shoppingcart(self, dt):
        self.timeout_event.cancel()
        self.on_start_timeout()
        self.shopping_cart_dialog.dismiss()

    #
    # When payment is not confirmed by user
    #
    def on_cancel_payment(self, dt):
        self.timeout_event.cancel()
        self.on_start_timeout()
        self.direct_confirm.dismiss()

    #
    # Confirms a payment
    #
    def on_confirm_payment(self, dt):
        # Serialize the shopping cart
        json_cart = self.shopping_cart.to_json()

        # use a POST-request to forward the shopping cart
        response = self.session.post(BackendURLs.CREATE_TRANSACTION.value, json=json_cart)

        if response.ok:
            # Reset instance variables
            self.__end_process()

            # Close the dialog
            self.direct_confirm.dismiss()

            # Return to the default screen for a new user to log in
            self.manager.current = Screens.DEFAULT_SCREEN.value

        else:
            Logger.critical("Payment could not be made: error: " + response.content)
            os._exit(1)

    def __end_process(self):
        self.shopping_cart.clear_cart()

        # Make sure to clear all products from each tab, as we need to reload them if we come back.
        for tab in self.tabs:
            for product_item in tab.ids.container.children:
                product_item.clear_item()

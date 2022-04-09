import os
import threading
import time
from asyncio import AbstractEventLoop
from typing import Dict, List

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

from ds.ShoppingCart import ShoppingCart, ShoppingCartListener
from scrs.TabDisplay import TabDisplay
from utils.Screens import Screens
from ux.CartDialog import CartDialog
from ux.ItemListUX import ItemListUX
from ux.ShoppingCartItem import ShoppingCartItem


class OnChangeShoppingCartListener(ShoppingCartListener):

    def __init__(self, product_screen):
        self.product_screen = product_screen

    def on_change(self):
        #self.product_screen.ids.buy_button.disabled = len(ProductScreen.shopping_cart.get_shopping_cart()) == 0
        self.product_screen.ids.shopping_cart_button.disabled = len(
            ProductScreen.shopping_cart.get_shopping_cart()) == 0


class ProductScreen(Screen):
    product_items_per_category: Dict[str, List[ItemListUX]] = {}

    tabs = []

    # shopping cart
    shopping_cart = ShoppingCart()

    def __init__(self, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Class level variables
        self.shopping_cart_dialog = None
        self.final_dialog = None

        # Timeout variables
        self.timeout_event = None
        self.timeout_time = 75

        self.event_loop: AbstractEventLoop = App.get_running_app().loop

        self.shopping_cart_listener = OnChangeShoppingCartListener(self)
        self.shopping_cart.add_listener(self.shopping_cart_listener)

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
    @mainthread
    def load_category_data(self):

        Logger.debug(f"StellaPayUI: Loading category data on thread {threading.current_thread().name}")

        start_time = time.time()

        if len(self.tabs) > 0:
            Logger.debug("StellaPayUI: Don't load tabs as we already have that information.")

            Logger.debug(f"StellaPayUI: Loaded category data and tabs (after skipping) in {time.time() - start_time} seconds")

            # Load product items (because we still need to reload them)
            self.load_products()

            return

        Logger.debug("StellaPayUI: Loading category view")

        def handle_product_data(product_data: Dict[str, List["Product"]]):
            for category in product_data.keys():
                # Create tab display
                tab = TabDisplay(text=category)
                self.ids.android_tabs.add_widget(tab)
                self.tabs.append(tab)

            Logger.debug(f"StellaPayUI: Loaded category data and tabs (no skipping) in {time.time() - start_time} seconds")

            # Load product items
            self.load_products()

        App.get_running_app().data_controller.get_product_data(callback=handle_product_data)

    def on_pre_enter(self, *args):
        # Initialize timeouts
        self.on_start_timeout()

    #
    # upon entering the screen, set the timeout
    #
    def on_enter(self, *args):

        # Set name of the active user in the toolbar (if there is one)
        self.ids.toolbar.title = \
            App.get_running_app().active_user if App.get_running_app().active_user is not None else "Stella Pay"

        # Load product data
        self.event_loop.call_soon_threadsafe(self.load_category_data)

    # Load product information and set up product view
    @mainthread
    def load_products(self):

        Logger.debug(f"StellaPayUI: Loading product data on thread {threading.current_thread().name}")

        start_time = time.time()

        # Check if we have tabs loaded
        if len(self.tabs) < 1:
            toast("There are no loaded tabs!")
            return

        if len(self.tabs[0].ids.container.children) > 0:
            Logger.debug("StellaPayUI: Don't load products view again as it's already there..")
            Logger.debug(f"Loaded products (after skipping) in {time.time() - start_time} seconds")
            return

        Logger.debug(f"StellaPayUI: Setting up product view")

        @mainthread
        def handle_product_data(product_data: Dict[str, List["Product"]]):
            for tab in self.tabs:
                for product in product_data[tab.text]:
                    # Get fun fact description of database
                    product_description = App.get_running_app().database_manager.get_random_fun_fact(product.get_name())

                    # Add item to the tab
                    tab.ids.container.add_widget(ItemListUX(text=product.get_name(), secondary_text=product_description,
                                                            secondary_theme_text_color="Custom",
                                                            secondary_text_color=[0.509, 0.509, 0.509, 1],
                                                            price="€" + product.get_price(),
                                                            shopping_cart=self.shopping_cart))

                # Add last item to the products (for each category) that is empty. This improves readability.
                tab.ids.container.add_widget(ItemListUX(text="", secondary_text="", secondary_theme_text_color="Custom",
                                                        secondary_text_color=[0.509, 0.509, 0.509, 1],
                                                        price=None,
                                                        shopping_cart=None))

                Logger.debug(f"Loaded products of category {tab.text} (no skipping) in {time.time() - start_time} seconds")
            Logger.debug(f"Loaded all products (no skipping) in {time.time() - start_time} seconds")

        App.get_running_app().data_controller.get_product_data(callback=handle_product_data)

    #
    # timeout callback function
    #
    def on_timeout(self, dt):
        self.end_user_session()

        # If the dialogs are instantiated, dismiss them before timeouts
        if self.shopping_cart_dialog:
            self.shopping_cart_dialog.dismiss()
        if ItemListUX.purchaser_list_dialog:
            ItemListUX.purchaser_list_dialog.dismiss()

        self.manager.current = Screens.DEFAULT_SCREEN.value

    #
    # upon leaving the screen, cancel the timeout event
    #
    def on_leave(self, *args):
        self.timeout_event.cancel()

    # Called when the user wants to leave this active session.
    def on_leave_product_screen_button(self):
        self.end_user_session()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = Screens.DEFAULT_SCREEN.value

    #
    # move to profile screen
    #
    def on_profile_screen(self):
        self.manager.transition = SlideTransition(direction="left")
        # Switch to profile screen
        self.manager.current = Screens.PROFILE_SCREEN.value

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
            self.shopping_cart_dialog = CartDialog(
                title="Wil je de aankoop afronden?",
                auto_dismiss=False,
                list_content=shopping_cart_items,
                buttons=[
                    MDFlatButton(
                        text="Nee",
                        on_release=self.on_close_shoppingcart
                    ),
                    MDRaisedButton(
                        text="Ja",
                        on_release=self.on_confirm_payment
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

    #
    # Confirms a payment
    #
    def on_confirm_payment(self, dt=None):
        Logger.info(f"StellaPayUI: Payment was confirmed by the user.")

        @mainthread
        def handle_transaction_result(success: bool):
            if success:
                # Reset instance variables
                self.end_user_session()

                if self.shopping_cart_dialog is not None:
                    self.shopping_cart_dialog.dismiss()

                self.timeout_event.cancel()

                self.final_dialog = MDDialog(
                    text="Gelukt! Je aankoop is geregistreerd",
                    buttons=[
                        MDRaisedButton(
                            text="Thanks",
                            on_release=self.on_thanks
                        ),
                    ]
                )

                self.timeout_event = Clock.schedule_once(self.on_thanks, 5)
                self.final_dialog.open()
            else:
                # Reset instance variables
                self.end_user_session()

                if self.shopping_cart_dialog is not None:
                    self.shopping_cart_dialog.dismiss()

                self.final_dialog = MDDialog(
                    text="Het is niet gelukt je aankoop te registreren. Herstart de app svp.",
                    buttons=[
                        MDRaisedButton(
                            text="Herstart",
                            on_release=(
                                os._exit(1)
                            )
                        ),
                    ]
                )
                self.final_dialog.open()

        # Make request to create transactions (on separate thread)
        App.get_running_app().loop.call_soon_threadsafe(
            App.get_running_app().data_controller.create_transactions, self.shopping_cart, handle_transaction_result)

    def on_thanks(self, _):
        if self.final_dialog is not None:
            self.final_dialog.dismiss()
            self.final_dialog = None

        # Return to the default screen for a new user to log in
        self.manager.current = Screens.DEFAULT_SCREEN.value

    # This method ought to be called when the user session is finished
    def end_user_session(self):
        # Clear shopping car
        self.shopping_cart.clear_cart()

        # Make sure to clear all products from each tab, as we need to reload them if we come back.
        for tab in self.tabs:
            for product_item in tab.ids.container.children:
                product_item.clear_item()

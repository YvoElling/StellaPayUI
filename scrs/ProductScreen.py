from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart
from scrs.TabDisplay import TabDisplay
from ux.ItemListUX import ItemListUX
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

    def __init__(self, cookies, **kwargs):
        # Load screen
        Builder.load_file('kvs/ProductScreen.kv')
        super(ProductScreen, self).__init__(**kwargs)

        # Class level variables
        self.direct_confirm = None
        # Shopping_cart dialog screen object
        self.shopping_cart_dialog = None
        self.requests_cookies = cookies

        # Timeout variables
        self.timeout_event = None
        self.timeout_time = 45

        # Get all categories names
        response = self.requests_cookies.get(url=self.get_all_cat_api)

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
                response = self.requests_cookies.get(request)

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

    # Start timeout counter
    def on_start_timeout(self):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    #
    # when the screen is touched, reset the timeout counter
    #
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.on_start_timeout()

    #
    # upon entering the screen, set the timeout
    #
    def on_enter(self, *args):
        # Initialize timeouts
        self.on_start_timeout()

        # For all items in the local_items list, add them to the container and display them
        for tab in self.tabs:
            for product in self.local_items[tab.text]:
                tab.ids.container.add_widget(ItemListUX(text=product.get_name(),
                                                        user_mail=self.manager.get_screen("DefaultScreen").user_mail,
                                                        price="€" + product.get_price(),
                                                        shoppingcart=self.shopping_cart,
                                                        cookies=self.requests_cookies,
                                                        secondary_text="Fun fact about " + product.get_name(),
                                                        secondary_theme_text_color="Custom",
                                                        secondary_text_color=[0.509, 0.509, 0.509, 1]))

    #
    # timeout callback function
    #
    def on_timeout(self, dt):
        self.__end_process()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # upon leaving the screen, cancel the timeout event
    #
    def on_leave(self, *args):
        for tab in self.tabs:
            tab.ids.container.clear_widgets()

    def on_cancel(self):
        self.timeout_event.cancel()
        self.__end_process()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # move to profile screen
    #
    def on_profile_screen(self):
        self.timeout_event.cancel()
        self.manager.current = 'ProfileScreen'

    #
    # callback function for when tab is switched
    #
    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        self.timeout_event.cancel()
        self.on_start_timeout()

    #
    # open confirmation dialog
    #
    def open_confirmation(self):
        # Restart timeout counter
        self.timeout_event.cancel()
        self.on_start_timeout()

        shopping_cart_items = self.shopping_cart.get_shopping_cart()

        if shopping_cart_items:
            # Create direct_confirm dialog
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
        # Reset timeout counter
        self.timeout_event.cancel()
        self.on_start_timeout()

        # Create an empty list that will contain all purchases
        shopping_cart_items = []

        # Retrieve all items from shopping cart and store in local shopping cart list
        for purchase in self.shopping_cart.get_shopping_cart():
            item = ShoppingCartItem(purchase=purchase,
                                    text=purchase.product_name,
                                    tertiary_text=" ",
                                    tertiary_theme_text_color="Custom",
                                    tertiary_text_color=[0.509, 0.509, 0.509, 1])
            shopping_cart_items.append(item)

        # If there are items in the shopping cart, display them
        if shopping_cart_items:
            self.shopping_cart_dialog = MDDialog(
                type="confirmation",
                items=shopping_cart_items,
                buttons=[
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
        self.timeout_event.cancel()
        self.on_start_timeout()
        self.shopping_cart_dialog.dismiss()

    #
    # Close dialog when TERUG is pressed
    #
    def on_return_direct_confirm(self, dt):
        self.timeout_event.cancel()
        self.on_start_timeout()
        self.direct_confirm.dismiss()

    #
    # Confirms a payment
    #
    def on_confirm(self, dt):
        # Serialize the shopping cart
        json_cart = self.shopping_cart.to_json()

        # use a POST-request to forward the shopping cart
        response = self.requests_cookies.post(self.confirm_api, json=json_cart)

        if response.ok:
            # Reset instance variables
            self.__end_process()

            # Stop timer
            self.timeout_event.cancel()

            # Close the dialog
            self.direct_confirm.dismiss()

            # Return to the default screen for a new user to log in
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = "DefaultScreen"

        else:
            print("Payment could not be made: error: " + response.content)
            exit(8)

    def __end_process(self):
        self.shopping_cart.emtpy_cart()


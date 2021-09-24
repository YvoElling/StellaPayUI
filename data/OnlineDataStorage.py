import threading
from collections import OrderedDict, defaultdict
from typing import Callable, Optional, List, Dict

from kivy import Logger
from kivy.app import App

from data.DataStorage import DataStorage
from ds.Product import Product
from utils import Connections


class OnlineDataStorage(DataStorage):

    def __init__(self):
        self.cached_user_data: OrderedDict[str, str] = OrderedDict()
        self.cached_product_data: Dict[str, List[Product]] = defaultdict(list)
        self.cached_category_data: List[str] = []

    def get_user_data(self, callback: Callable[[Optional[Dict[str, str]]], None] = None) -> None:

        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_user_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) user data")
            # Return cached user data
            callback(self.cached_user_data)
            return

        Logger.debug(f"StellaPayUI: Loading user mapping on thread {threading.current_thread().name}")

        user_data = App.get_running_app().session_manager.do_get_request(url=Connections.get_users())

        if user_data and user_data.ok:
            # convert to json
            user_json = user_data.json()

            # append json to list and sort the list
            for user in user_json:
                # store all emails adressed in the sheet_menu
                self.cached_user_data[user["name"]] = user["email"]

            # Sort items
            self.cached_user_data = OrderedDict(sorted(self.cached_user_data.items()))

            Logger.debug("StellaPayUI: Loaded user data")

            callback(self.cached_user_data)
        else:
            Logger.critical("StellaPayUI: Error: users could not be fetched from the online database")
            callback(None)

    def get_product_data(self, callback: Callable[[Optional[Dict[str, List[Product]]]], None] = None) -> None:
        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_product_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) product data")
            # Return cached product data
            callback(self.cached_product_data)
            return

        # Check if there is category data loaded. We need that, otherwise we can't load the products.
        if len(self.cached_category_data) < 1:
            Logger.warning("StellaPayUI: Cannot load product data because there is no (cached) category data!")
            callback(None)
            return

        Logger.debug(f"StellaPayUI: Loading product data on thread {threading.current_thread().name}")

        # Grab products from each category
        for category in self.cached_category_data:
            # Request products from each category
            request = Connections.get_products() + category
            product_data = App.get_running_app().session_manager.do_get_request(request)

            if product_data and product_data.ok:
                # convert to json
                products = product_data.json()

                Logger.debug(f"StellaPayUI: Retrieved {len(products)} products for category '{category}'")

                # Create a product object for all products
                for product in products:
                    # Only add the product to the list if the product must be shown
                    if product['shown']:
                        p = Product().create_from_json(product)
                        self.cached_product_data[category].append(p)

            else:
                Logger.warning(f"StellaPayUI: Error: could not fetch products for category {category}.")
                return

        # Make sure to call the callback with the proper data. (None if we have no data).
        if len(self.cached_product_data) > 0:
            callback(self.cached_product_data)
        else:
            callback(None)

    def get_category_data(self, callback: Callable[[Optional[List[str]]], None] = None) -> None:
        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_category_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) category data")
            # Return cached category data
            callback(self.cached_category_data)
            return

        Logger.debug(f"StellaPayUI: Loading category data on thread {threading.current_thread().name}")

        # Do request to the correct URL
        category_data = App.get_running_app().session_manager.do_get_request(url=Connections.get_categories())

        if category_data and category_data.ok:
            # convert to json
            categories = category_data.json()

            for category in categories:
                self.cached_category_data.append(str(category['name']))

            Logger.debug("StellaPayUI: Loaded category data")

            callback(self.cached_category_data)
        else:
            Logger.critical("StellaPayUI: Error: categories could not be fetched from the online database")
            callback(None)

import threading
import traceback
from collections import OrderedDict
from typing import Callable, Optional, List, Dict

from kivy import Logger
from kivy.app import App

from data.CachedDataStorage import CachedDataStorage
from data.DataStorage import DataStorage
from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart
from utils import Connections


class OnlineDataStorage(DataStorage):

    def __init__(self, cached_data_storage: CachedDataStorage):
        self.cached_data_storage = cached_data_storage

    def get_user_data(self, callback: Callable[[Optional[Dict[str, str]]], None] = None) -> None:

        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_data_storage.cached_user_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) user data")
            # Return cached user data
            callback(self.cached_data_storage.cached_user_data)
            return

        Logger.debug(f"StellaPayUI: Loading user mapping on thread {threading.current_thread().name}")

        user_data = App.get_running_app().session_manager.do_get_request(url=Connections.get_users())

        if user_data and user_data.ok:
            # convert to json
            user_json = user_data.json()

            # append json to list and sort the list
            for user in user_json:
                # store all emails addressed in the sheet_menu
                self.cached_data_storage.cached_user_data[user["name"]] = user["email"]

            # Sort items
            self.cached_data_storage.cached_user_data = OrderedDict(
                sorted(self.cached_data_storage.cached_user_data.items()))

            Logger.debug("StellaPayUI: Loaded user data")

            callback(self.cached_data_storage.cached_user_data)
        else:
            Logger.critical("StellaPayUI: Error: users could not be fetched from the online database")
            callback(None)

    def get_product_data(self, callback: Callable[[Optional[Dict[str, List[Product]]]], None] = None) -> None:
        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_data_storage.cached_product_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) product data")
            # Return cached product data
            callback(self.cached_data_storage.cached_product_data)
            return

        # Check if there is category data loaded. We need that, otherwise we can't load the products.
        if len(self.cached_data_storage.cached_category_data) < 1:
            Logger.warning("StellaPayUI: Cannot load product data because there is no (cached) category data!")
            callback(None)
            return

        Logger.debug(f"StellaPayUI: Loading product data on thread {threading.current_thread().name}")

        # Grab products from each category
        for category in self.cached_data_storage.cached_category_data:
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
                        self.cached_data_storage.cached_product_data[category].append(p)

            else:
                Logger.warning(f"StellaPayUI: Error: could not fetch products for category {category}.")
                return

        # Make sure to call the callback with the proper data. (None if we have no data).
        if len(self.cached_data_storage.cached_product_data) > 0:
            callback(self.cached_data_storage.cached_product_data)
        else:
            callback(None)

    def get_category_data(self, callback: Callable[[Optional[List[str]]], None] = None) -> None:
        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_data_storage.cached_category_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) category data")
            # Return cached category data
            callback(self.cached_data_storage.cached_category_data)
            return

        Logger.debug(f"StellaPayUI: Loading category data on thread {threading.current_thread().name}")

        # Do request to the correct URL
        category_data = App.get_running_app().session_manager.do_get_request(url=Connections.get_categories())

        if category_data and category_data.ok:
            # convert to json
            categories = category_data.json()

            for category in categories:
                self.cached_data_storage.cached_category_data.append(str(category['name']))

            Logger.debug("StellaPayUI: Loaded category data")

            callback(self.cached_data_storage.cached_category_data)
        else:
            Logger.critical("StellaPayUI: Error: categories could not be fetched from the online database")
            callback(None)

    def get_card_info(self, card_id=None, callback: Callable[[Optional[NFCCardInfo]], None] = None) -> None:

        if card_id is None:
            callback(None)
            return

        # Check if we have cached card info already
        if card_id in self.cached_data_storage.cached_card_info:
            # Return the cached data
            callback(self.cached_data_storage.cached_card_info[card_id])
            return

        Logger.debug(f"StellaPayUI: Loading card data on thread {threading.current_thread().name}")

        # Do request to the correct URL
        cards_data = App.get_running_app().session_manager.do_get_request(url=Connections.get_all_cards())

        # Check if we have valid card data
        if cards_data and cards_data.ok:
            # convert to json
            cards = cards_data.json()

            # Loop over every card and store the information in the cache
            for card in cards:
                # store user-mail for payment confirmation later
                user_mail = card["owner"]["email"]
                user_name = card["owner"]["name"]
                card_data_id = card["card_id"]

                # Create card info object
                card_info = NFCCardInfo(card_id=card_data_id, owner_email=user_mail, owner_name=user_name)

                # Cache card info for later use
                self.cached_data_storage.cached_card_info[card_data_id] = card_info

            Logger.debug("StellaPayUI: Loaded cards data")

            # Return the loaded card data to the user
            callback(self.cached_data_storage.cached_card_info[card_id])
        else:
            Logger.critical("StellaPayUI: Error: cards could not be fetched from the online database")
            callback(None)

    def register_card_info(self, card_id: str = None, email: str = None, owner: str = None,
                           callback: [[bool], None] = None) -> None:
        # Check if we have a card id and email
        if card_id is None or email is None:
            if callback is not None:
                callback(False)
            return

        # Check if they are not empty strings
        if len(card_id) < 1 or len(email) < 1:
            if callback is not None:
                callback(False)
            return

        # Use a POST command to add connect this UID to the user
        request = App.get_running_app().session_manager.do_post_request(url=Connections.add_user_mapping(),
                                                                        json_data={'card_id': card_id,
                                                                                   'email': email})

        Logger.debug(f"StellaPayUI: Registering new card on {threading.current_thread().name}")

        # If the user was added successfully ( status_code : 200),
        if request.ok:
            Logger.info(f"StellaPayUI: Registered new card with id {card_id} for {email}")

            if callback is not None:
                callback(True)
            return
        else:
            # User could not be added succesfully, give error 2.
            Logger.warning(f"StellaPayUI: Could not register new card with id {card_id} for {owner}, error: "
                           f"{request.text}")

            if callback is not None:
                callback(False)
            return

    def create_transactions(self, shopping_cart: ShoppingCart = None, callback: Callable[[bool], None] = None) -> None:
        # Check if we have a shopping cart
        if shopping_cart is None:
            if callback is not None:
                callback(False)
            return

        # Check if the shopping cart is empty. If so, we return true (since all transactions have been registered).
        if len(shopping_cart.basket) < 1:
            if callback is not None:
                callback(True)
            return

        try:
            json_cart = shopping_cart.to_json()
        except Exception as e:
            Logger.warning("StellaPayUI: There was an error while parsing the shopping cart to JSON!")
            traceback.print_exception(None, e, e.__traceback__)

            if callback is not None:
                callback(False)
            return

        # use a POST-request to forward the shopping cart
        response = App.get_running_app().session_manager.do_post_request(url=Connections.create_transaction(),
                                                                         json_data=json_cart)

        # Response was okay.
        if response and response.ok:
            Logger.info(f"StellaPayUI: Registered {len(shopping_cart.basket)} transactions to the server.")
            if callback is not None:
                callback(True)
            return
        elif not response.ok:
            Logger.warning(f"StellaPayUI: Failed to register {len(shopping_cart.basket)} transactions to the server.")
            # Response was wrong
            if callback is not None:
                callback(False)
        else:
            Logger.critical(f"StellaPayUI: Payment could not be made: error: {response.content}")
            if callback is not None:
                callback(False)

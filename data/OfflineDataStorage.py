import json
import os
import threading
import traceback
from collections import OrderedDict
from typing import Callable, Optional, List, Dict, Any

from kivy import Logger

from data.CachedDataStorage import CachedDataStorage
from data.DataStorage import DataStorage
from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart


class OfflineDataStorage(DataStorage):
    # Path and name of file to store cache.
    CACHE_FILE_NAME = "cached_data.json"

    # Path and name to file that stores data that should still be uploaded to the backend
    # When the system is in offline mode, it will write to this file. Once internet connection has been restored, we can
    # start emptying this file and uploading it to the backend.
    PENDING_DATA_FILE_NAME = "pending_data.json"

    def __init__(self, cached_data_storage: CachedDataStorage):
        self.cached_data_storage = cached_data_storage

        # Contains the cached json data so we don't need to keep reading the file.
        self.cached_json_data = self.__get_json_data_from_file__(OfflineDataStorage.CACHE_FILE_NAME)

        # Load pending data file into memory
        self.pending_json_data = self.__get_json_data_from_file__(OfflineDataStorage.PENDING_DATA_FILE_NAME)

    def get_user_data(self, callback: Callable[[Optional[Dict[str, str]]], None] = None) -> None:

        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        # Check if we have a cached version of this somewhere
        if len(self.cached_data_storage.cached_user_data) > 0:
            Logger.debug("StellaPayUI: Using offline (cached) user data")
            # Return cached user data
            callback(self.cached_data_storage.cached_user_data)
            return

        Logger.debug(f"StellaPayUI: Loading user mapping on thread {threading.current_thread().name}")

        try:
            users = self.cached_json_data["users"]

            for username, user_data in users.items():
                self.cached_data_storage.cached_user_data[username] = user_data["email"]

            # Sort items
            self.cached_data_storage.cached_user_data = OrderedDict(
                sorted(self.cached_data_storage.cached_user_data.items()))

            Logger.debug("StellaPayUI: Loaded user data")

            callback(self.cached_data_storage.cached_user_data)
        except Exception as e:
            Logger.critical(f"StellaPayUI: A problem with retrieving offline user data!")
            traceback.print_exception(None, e, e.__traceback__)

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

        Logger.debug(f"StellaPayUI: Loading product data on thread {threading.current_thread().name}")

        # Grab products from storage file
        try:
            # Load products section
            products = self.cached_json_data["products"]

            # Load product data
            for product, product_data in products.items():
                category_name = product_data["category"]
                shown = product_data["shown"]
                price = product_data["price"]

                # Add product to cache
                self.cached_data_storage.cached_product_data[category_name] \
                    .append(Product().create_from_json(json={"name": product, "price": price, "shown": shown}))

            Logger.debug(f"StellaPayUI: Retrieved {len(products)} products from offline storage")

            callback(self.cached_data_storage.cached_product_data)
        except Exception as e:
            Logger.critical(f"StellaPayUI: A problem with retrieving offline product data!")
            traceback.print_exception(None, e, e.__traceback__)

            callback(None)

    def get_category_data(self, callback: Callable[[Optional[List[str]]], None] = None) -> None:
        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_data_storage.cached_category_data) > 0:
            Logger.debug("StellaPayUI: Using offline (cached) category data")
            # Return cached category data
            callback(self.cached_data_storage.cached_category_data)
            return

        Logger.debug(f"StellaPayUI: Loading category data on thread {threading.current_thread().name}")

        # Grab categories from storage file
        try:
            # Load category section
            categories = self.cached_json_data["categories"]

            # Load category data
            for category in categories:
                self.cached_data_storage.cached_category_data.append(str(category))

            Logger.debug(f"StellaPayUI: Retrieved {len(categories)} categories from offline storage")

            callback(self.cached_data_storage.cached_category_data)
        except Exception as e:
            Logger.critical(f"StellaPayUI: A problem with retrieving offline category data!")
            traceback.print_exception(None, e, e.__traceback__)

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

        Logger.debug(f"StellaPayUI: Loading data of card {card_id} data on thread {threading.current_thread().name}")

        # Grab card info from storage file
        try:
            # Load cards section
            cards = self.cached_json_data["cards"]

            if len(cards) < 1:
                callback(None)
                return

            # Load cards data
            for card, card_data in cards.items():
                card_owner = str(card_data["owner"])
                card_email = str(card_data["email"])

                # Create card info object
                card_info = NFCCardInfo(card_id=card_id, owner_email=card_email, owner_name=card_owner)

                # Cache card info for later use
                self.cached_data_storage.cached_card_info[card_id] = card_info

            Logger.debug(f"StellaPayUI: Retrieved {len(cards)} cards from offline storage")

            # Since we've loaded all cards, now check if the one we're looking for is present
            if card_id in self.cached_data_storage.cached_card_info:
                # Return the cached data
                callback(self.cached_data_storage.cached_card_info[card_id])
                return
            else:
                # We couldn't find the card
                callback(None)
                return

        except Exception as e:
            Logger.critical(f"StellaPayUI: A problem with retrieving offline card data!")
            traceback.print_exception(None, e, e.__traceback__)

            callback(None)

    def register_card_info(self, card_id: str = None, email: str = None, owner: str = None,
                           callback: Callable[[bool], None] = None) -> None:
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

        # Check if we have a cards section. If not, create it.
        if "cards" not in self.pending_json_data:
            self.pending_json_data["cards"] = {}

        # Add new card and email address to the pending data
        self.pending_json_data["cards"][card_id] = {"email": email, "owner": owner}

        # Add new card mapping to cache so we detect it at a later stage
        card_info = NFCCardInfo(card_id=card_id, owner_email=email, owner_name=owner)
        self.cached_data_storage.cached_card_info[card_id] = card_info

        Logger.debug(f"StellaPayUI: Registering (offline) new card on {threading.current_thread().name}")

        # Save new pending data
        if self.__save_json_data_to_file__(self.pending_json_data, OfflineDataStorage.PENDING_DATA_FILE_NAME):
            Logger.info(f"StellaPayUI: Registered (offline) new card with id {card_id} for {email}")

            if callback is not None:
                callback(True)
            return
        else:
            # User could not be added succesfully, give error 2.
            Logger.warning(f"StellaPayUI: Could not register (offline) new card with id {card_id} for {email}")

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

        # Check if we have a transactions section. If not, create it.
        if "transactions" not in self.pending_json_data:
            self.pending_json_data["transactions"] = []

        # Grab products from shopping cart
        transactions = json_cart["products"]

        # Add the transactions of the shopping cart to the pending data
        self.pending_json_data["transactions"].extend(transactions)

        # Save new pending data
        if self.__save_json_data_to_file__(self.pending_json_data, OfflineDataStorage.PENDING_DATA_FILE_NAME):
            Logger.info(f"StellaPayUI: Registered {len(shopping_cart.basket)} transactions to the pending data.")

            if callback is not None:
                callback(True)
            return
        else:
            Logger.warning(
                f"StellaPayUI: Failed to register {len(shopping_cart.basket)} transactions to the pending data.")

            if callback is not None:
                callback(False)
            return

    def __save_json_data_to_file__(self, json_data: Dict, path_to_file: str = None) -> bool:
        """
        Save JSON data to a file.
        :param json_data: Data to store
        :param path_to_file: Path to file (including file name).
        :return: true when the file has been successfully saved, false otherwise
        """

        # Check if we have a path given
        if path_to_file is None:
            path_to_file = OfflineDataStorage.CACHE_FILE_NAME

        try:
            with open(path_to_file, "w") as file:
                json.dump(json_data, file, indent=4)  # Try to write the JSON data to the file
                return True
        except Exception as e:
            Logger.critical(f"StellaPayUI: Could not save cached JSON data!")
            traceback.print_exception(None, e, e.__traceback__)
            return False

    def update_file_from_cache(self) -> None:
        """
        This method retrieves the data that is stored in the cache manager and stores it in the json file. This method
        can be run periodically to refresh the file every once in a while.
        """

        Logger.debug(
            f"StellaPayUI: Updating offline storage from data in the cache (on thread {threading.current_thread().name})!")

        json_data_to_store = dict()

        # Create users section
        json_data_to_store["users"] = dict()

        # Create products section
        json_data_to_store["products"] = dict()

        # Create category section
        json_data_to_store["categories"] = []

        # Create card section
        json_data_to_store["cards"] = dict()

        # Specify users section
        for user, email in self.cached_data_storage.cached_user_data.items():
            user_data = dict()
            user_data["email"] = email
            json_data_to_store["users"][user] = user_data

        # Specify products section
        for category_name, products in self.cached_data_storage.cached_product_data.items():
            for product in products:
                product_data = dict()
                product_data["price"] = product.get_price()
                product_data["shown"] = "true"
                product_data["category"] = category_name
                json_data_to_store["products"][product.get_name()] = product_data
            # Add category name to json file as well
            json_data_to_store["categories"].append(category_name)

        # Specify cards section
        for card_id, card_info in self.cached_data_storage.cached_card_info.items():
            card_data = dict()
            card_data["owner"] = card_info.owner_name
            card_data["email"] = card_info.owner_email

            # Store card in cards section
            json_data_to_store["cards"][card_id] = card_data

        # Store the JSON file
        self.__save_json_data_to_file__(json_data_to_store)

    def __get_json_data_from_file__(self, file_path: str = None) -> Optional[Any]:
        """
        Load a JSON file and return the data in JSON format.
        It will create the requested file if it does not exist. Will return None if file could not be read by the JSON
        parser
        """

        # Check if we have a path given
        if file_path is None:
            file_path = OfflineDataStorage.CACHE_FILE_NAME

        try:
            # Try to create a file (if it does not exist)
            if not os.path.exists(file_path):
                open(file_path, "w").close()

            with open(file_path, "r") as cached_json_data:
                json_data = json.load(cached_json_data)  # Load cached data into memory
                Logger.debug(f"StellaPayUI: Loaded offline file {file_path}")

                # Make it an empty dictionary if no data was available in the file
                if json_data is None:
                    json_data = {}

                return json_data
        except FileNotFoundError as error:
            Logger.critical(f"StellaPayUI: Could not find {file_path}. Creating one.")
        except Exception as e:
            Logger.critical(f"StellaPayUI: A problem with loading JSON data from {file_path}!")
            traceback.print_exception(None, e, e.__traceback__)

        # Return empty dict since the file contains no data
        return {}

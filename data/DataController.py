import json
from json import JSONDecodeError
from threading import Thread
from typing import Callable, Optional, Dict, List

import requests
from kivy import Logger
from kivy.app import App

from data.CachedDataStorage import CachedDataStorage
from data.ConnectionListener import ConnectionListener
from data.OfflineDataStorage import OfflineDataStorage
from data.OnlineDataStorage import OnlineDataStorage
from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart
from utils import Connections


class DataController:
    """
    This class is responsible for loading and storing data that the application needs. This might be user data or
    product data.

    This class should be used to retrieve data as it hides where it gets the data from (either offline or online
    storage). The DataController is responsible for deciding where the info comes from.

    """

    def __init__(self):
        self.cached_data_storage = CachedDataStorage()
        self.online_data_storage = OnlineDataStorage(self.cached_data_storage)
        self.offline_data_storage = OfflineDataStorage(self.cached_data_storage)
        self.can_use_online_database = False

        # Listeners that want to know about a change in connection
        self.on_connection_change_listeners: List[ConnectionListener] = []

    def start_connection_update_thread(self, url: str = None):
        # Create a thread to update connection status
        self.connection_update_thread = Thread(target=self.__update_connection_status__, args=(url,))

        # Start the thread
        self.connection_update_thread.start()

    def get_user_data(self, callback: Callable[[Optional[Dict[str, str]]], None] = None) -> None:
        """
        Get a mapping of all users and their e-mail addresses. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The user data is returned as a dictionary, where the key (str) is the username and the corresponding value (str)
        is the associated e-mail address.

        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents a dictionary of users. This might also be None!

        :return: Nothing.
        """

        # Pass the callback to the appropriate method.
        if self.running_in_online_mode():
            self.online_data_storage.get_user_data(callback=callback)
        else:
            self.offline_data_storage.get_user_data(callback=callback)

    def get_product_data(self, callback: Callable[[Optional[Dict[str, List[Product]]]], None] = None) -> None:
        """
        Get a list of all products (in their categories). Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The product data is returned as a map, where each key is a category name and the value a list of Product objects.

        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents the map. This might also be None!

        :return: Nothing.
        """
        # Pass the callback to the appropriate method.
        if self.running_in_online_mode():
            self.online_data_storage.get_product_data(callback=callback)
        else:
            self.offline_data_storage.get_product_data(callback=callback)

    def get_category_data(self, callback: Callable[[Optional[List[str]]], None] = None) -> None:
        """
        Get a list of all categories. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The category data is returned as a list, where each element is the name of category (as a string).

        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents a list of categories. This might also be None!

        :return: Nothing.
        """
        # Pass the callback to the appropriate method.
        if self.running_in_online_mode():
            self.online_data_storage.get_category_data(callback=callback)
        else:
            self.offline_data_storage.get_category_data(callback=callback)

    def get_card_info(self, card_id=None, callback: Callable[[Optional[NFCCardInfo]], None] = None) -> None:
        """
        Get info of a particular card. Note that you'll need to provide a callback function
        that will be called whenever the data is available. The callback will also be called when no data is available.

        The card info will be returned as a NFCCardInfo object.

        :param card_id: id of the card
        :param callback: Method called when this method is finished retrieving data. The callback will have one argument
            that represents the card info. This might also be None!
        :return: Nothing.
        """
        # Pass the callback to the appropriate method.
        if self.running_in_online_mode():
            self.online_data_storage.get_card_info(card_id=card_id, callback=callback)
        else:
            self.offline_data_storage.get_card_info(card_id=card_id, callback=callback)

    def register_card_info(self, card_id: str = None, email: str = None, owner: str = None,
                           callback: Callable[[bool], None] = None) -> None:
        """
        Register a new card for a particular user.
        :param card_id: Id of the card to register
        :param email: E-mail address of the user that you want to match this card with.
        :param owner: Name of the owner of the card
        :param callback: Method called when this method is finished. The callback will have one argument (boolean)
            that indicates whether the card has been registered (true) or not (false).
        :return: Nothing
        """
        # Pass the callback to the appropriate method.
        if self.running_in_online_mode():
            self.online_data_storage.register_card_info(card_id=card_id, email=email, owner=owner, callback=callback)
        else:
            self.offline_data_storage.register_card_info(card_id=card_id, email=email, owner=owner, callback=callback)

    def create_transactions(self, shopping_cart: ShoppingCart = None, callback: Callable[[bool], None] = None) -> None:
        """
        Create a transaction (or multiple) of goods. Note that you'll need to provide a callback function
        that will be called whenever the call is completed.

        :param shopping_cart: Shopping cart that has all transactions you want to create
        :param callback: Method called when this method is finished. The callback will have one argument (boolean)
            that indicates whether the transactions have been registered (true) or not (false).
        :return: Nothing
        """
        # Pass the callback to the appropriate method.

        if self.running_in_online_mode():
            self.online_data_storage.create_transactions(shopping_cart=shopping_cart, callback=callback)
        else:
            self.offline_data_storage.create_transactions(shopping_cart=shopping_cart, callback=callback)

    @staticmethod
    def __is_online_database_reachable__(url: str = Connections.hostname, timeout: int = 5) -> bool:
        try:
            req = requests.head(url, timeout=timeout)
            # HTTP errors are not raised by default, this statement does that
            req.raise_for_status()
            return True
        except requests.HTTPError as e:
            print("Checking internet connection failed, status code {0}.".format(
                e.response.status_code))
        except requests.ConnectionError:
            # print("No internet connection available.")
            pass
        return False

    def __update_connection_status__(self, url: str = None) -> None:
        """
        This method continuously checks whether a connection to the online database is possible. Note that this method
        should be called only once and another thread as it will block periodically.
        """
        connection_status = DataController.__is_online_database_reachable__(url=url)

        # If we could not connect before, but we did now, let's make sure to tell!
        if not self.can_use_online_database and connection_status:
            Logger.debug(f"StellaPayUI: Connected to online database (again)!")

            # Notify all listeners
            for listener in self.on_connection_change_listeners:
                listener.on_connection_change(True)

        # If we had connection, but lost it, let's tell that as well.
        elif self.can_use_online_database and not connection_status:
            Logger.warning(f"StellaPayUI: Lost connection to the online database!")

            # Notify all listeners
            for listener in self.on_connection_change_listeners:
                listener.on_connection_change(False)

        self.can_use_online_database = connection_status

        App.get_running_app().loop.call_later(10, self.__update_connection_status__, url)

    def __update_offline_storage__(self) -> None:
        """
        This method runs in a different thread and runs the updater of the offline storage periodically.
        It also makes sure to write any pending data to the backend if there is a connection
        """
        # Update JSON file with what's currently in the cache.
        self.offline_data_storage.update_file_from_cache()

        # After updating the offline storage, let's check if we can send pending data
        self.__send_pending_data_to_online_server__()

        # Make sure to run another call in a few minutes again
        App.get_running_app().loop.call_later(5 * 60, self.__update_offline_storage__)

    def __send_pending_data_to_online_server__(self) -> None:
        """
        This method will look in the pending data file to see if there are entries that need to registered at the online
        server. If that is the case, the entries will be registered and subsequently removed from the pending data.

        This mechanism makes sure that any transactions that were performed when the device was offline are still
        transmitted to the server eventually.
        """

        # Check if we have an internet connection
        if not self.can_use_online_database:
            return

        Logger.debug(f"StellaPayUI: Searching for pending transactions to register at the online server.")

        # JSON data that were going to write to the pending data.
        json_data_to_write = None

        with open(OfflineDataStorage.PENDING_DATA_FILE_NAME, "r") as pending_data_file:
            try:
                pending_data_json = json.load(pending_data_file)  # Load cached data into memory
                Logger.debug(f"StellaPayUI: Loaded pending data file")
            except JSONDecodeError:
                Logger.critical(f"StellaPayUI: Could not read JSON from {OfflineDataStorage.PENDING_DATA_FILE_NAME}")
                pending_data_json = None

            # If we cannot read the file, let's stop right here.
            if pending_data_json is None:
                return

            # We have transaction data to send
            if "transactions" in pending_data_json:
                # Create json object that mimics the format we need to be able to read it as a shopping cart
                adjusted_json_data = {"products": []}

                # Add the transactions to the products
                adjusted_json_data["products"].extend(pending_data_json["transactions"])

                # Make a shopping cart from the products
                shopping_cart = ShoppingCart.from_json(adjusted_json_data)

                # If we have a valid shopping cart and it's not empty
                if shopping_cart is not None and len(shopping_cart.basket) > 0:
                    # We send it to the online server
                    self.create_transactions(shopping_cart, lambda success: Logger.debug(
                        f"StellaPayUI: Registered {len(shopping_cart.basket)} new transactions from pending data: {success}"))

            # Remove all transactions from the pending data
            pending_data_json["transactions"] = []

            # Store which card_ids were successfully registered
            cards_registered_successfully = []

            # We have card data to send
            if "cards" in pending_data_json:
                for card_id in pending_data_json["cards"]:
                    card_info = pending_data_json["cards"][card_id]

                    # Ignore this invalid card
                    if card_info is None:
                        continue

                    # Ignore a card that has no email attached to it
                    if "email" not in card_info:
                        continue

                    # Register card
                    self.register_card_info(card_id=card_id, email=card_info["email"], owner=None,
                                            callback=lambda success: cards_registered_successfully.append(
                                                card_id if success else None))

            # Determine which cards were validly registered (and hence can be removed from the pending data)
            valid_cards = list(filter((lambda card: card is not None), cards_registered_successfully))

            # Remove cards that were successfully added.
            for valid_card_id in valid_cards:
                pending_data_json["cards"].pop(valid_card_id, None)

            Logger.debug(f"StellaPayUI: Registered {len(valid_cards)} cards from pending data")

            # Make sure to copy the pending data to a new JSON object so we can use it outside the 'with' statement.
            json_data_to_write = pending_data_json

        # Finally write the new JSON data to the pending data file
        with open(OfflineDataStorage.PENDING_DATA_FILE_NAME, 'w') as data_file:
            json.dump(json_data_to_write, data_file, indent=4)

    # Get whether we can connect to the backend or not
    def running_in_online_mode(self) -> bool:
        return self.can_use_online_database

    # Run the setup procedure, i.e. check whether we can connect to remote server
    # If we can connect, we start authentication, otherwise we run in offline mode.
    # Make sure to run this method in a separate thread because it will be blocking.
    def start_setup_procedure(self):
        if self.running_in_online_mode():
            Logger.critical(f"StellaPayUI: Running in ONLINE mode!")
            # Start up authentication
            App.get_running_app().loop.call_soon_threadsafe(App.get_running_app().session_manager.setup_session,
                                                            App.get_running_app().done_loading_authentication)
        else:
            # We need to run in offline mode. Do not run authentication to the backend (as it will fail anyway).
            Logger.critical(f"StellaPayUI: Running in OFFLINE mode!")

            App.get_running_app().loop.call_soon_threadsafe(App.get_running_app().done_loading_authentication)

        # Thread to keep updating the offline storage files with data from the caching manager
        App.get_running_app().loop.call_later(60, self.__update_offline_storage__)

    def register_connection_listener(self, connection_listener: ConnectionListener) -> None:
        """
        Register a listener that will be notified when a connection to the backend could be made, or was lost.
        :param connection_listener: Listener to be notified
        """
        self.on_connection_change_listeners.append(connection_listener)

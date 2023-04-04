import asyncio
import json
import sys
import threading
import time
from datetime import datetime
from json import JSONDecodeError
from threading import Thread
from typing import Optional, Dict, List

import requests
from kivy import Logger
from kivy.app import App

from data.CachedDataStorage import CachedDataStorage
from data.ConnectionListener import ConnectionListener
from data.OfflineDataStorage import OfflineDataStorage
from data.OnlineDataStorage import OnlineDataStorage
from data.user.user_data import UserData
from ds.NFCCardInfo import NFCCardInfo
from ds.Product import Product
from ds.ShoppingCart import ShoppingCart
from utils import Connections, ConfigurationOptions
from utils.ConfigurationOptions import ConfigurationOption


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
        self.connection_update_thread = Thread(target=self._update_connection_status, args=(url,), daemon=True)

        # Start the thread
        self.connection_update_thread.start()

    async def get_user_data(self) -> List[UserData]:
        """
        Get a mapping of all users and their e-mail addresses. Note that is an asynchronous method that needs to be awaited.

        The user data is as a list of `UserData` objects, containing the user's name and email address.

        :return: a list of known users
        """
        if self.running_in_online_mode():
            return await self.online_data_storage.get_user_data()
        else:
            return await self.offline_data_storage.get_user_data()

    async def get_product_data(self) -> Dict[str, List[Product]]:
        """
        Get a list of all products in their corresponding categories. Note that this is an asynchronous method and needs
        to be awaited!

        :return: a dictionary is returned where the key is a category name and the value a list of products in that category
        """
        if self.running_in_online_mode():
            return await self.online_data_storage.get_product_data()
        else:
            return await self.offline_data_storage.get_product_data()

    async def get_category_data(self) -> List[str]:
        """
        Get a list of all categories Note that this is an asynchronous method and needs to be awaited!

        :return: a list of categories
        """
        if self.running_in_online_mode():
            return await self.online_data_storage.get_category_data()
        else:
            return await self.offline_data_storage.get_category_data()

    async def get_card_info(self, card_id) -> Optional[NFCCardInfo]:
        """
        Get info of a particular card. Note that this method is asynchronous and thus needs to be awaited.

        The card info will be returned as a `NFCCardInfo` object.

        :param card_id: Id of the card to look for
        :return: a `NFCCardInfo` object if matching the given ``card_id`` or None if nothing could be found
        """
        if self.running_in_online_mode():
            return await self.online_data_storage.get_card_info(card_id=card_id)
        else:
            return await self.offline_data_storage.get_card_info(card_id=card_id)

    async def register_card_info(self, card_id: str, email: str, owner: str) -> bool:
        """
        Register a new card for a particular user. Note that this is an asynchronous method and thus must be awaited!

        :param card_id: Id of the card to register
        :param email: E-mail address of the user that you want to match this card with.
        :param owner: Name of the owner of the card
        :return: Whether the card has successfully been registered.
        """
        # Pass the callback to the appropriate method.
        if self.running_in_online_mode():
            return await self.online_data_storage.register_card_info(card_id=card_id, email=email, owner=owner)
        else:
            return await self.offline_data_storage.register_card_info(card_id=card_id, email=email, owner=owner)

    async def create_transactions(self, shopping_cart: ShoppingCart) -> bool:
        """
        Create a transaction (or multiple) of goods. Note that this is an asynchronous method and thus must be awaited!

        :param shopping_cart: Shopping cart that has all transactions you want to create
        :return: Whether the transactions have been registered (true) or not (false).
        """
        if self.running_in_online_mode():
            return await self.online_data_storage.create_transactions(shopping_cart=shopping_cart)
        else:
            return await self.offline_data_storage.create_transactions(shopping_cart=shopping_cart)

    async def get_recent_users(self, number_of_unique_users: int = 3) -> List[str]:
        """
        Get the most recent users that have bought something since the start of the current day. This method
        will only work when we are connected to the internet. Note that this method is asynchronous and thus
        needs to be awaited.

        :param number_of_unique_users: The number of unique users to return. If there are fewer than
            the requested amount, all of them are returned.
        :return: a list of names of users that bought something, in order of their purchase time.
        """
        # This is not supported when running in offline mode
        if not self.running_in_online_mode():
            return []

        Logger.debug(f"StellaPayUI: ({threading.current_thread().name}) Loading most recent users")

        # Get today, and set time to midnight.
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        response = await App.get_running_app().session_manager.do_post_request_async(
            url=Connections.get_all_transactions(), json_data={"begin_date": today.strftime("%Y/%m/%d %H:%M:%S")}
        )

        if response is None or not response.ok:
            return []

        try:
            body = json.loads(response.content)
        except:
            Logger.warning("StellaPayUI: Failed to parse most recent users query")
            return []

        ignored_addresses = [
            "onderhoud@solarteameindhoven.nl",
            "beheer@solarteameindhoven.nl",
            "info@solarteameindhoven.nl",
        ]

        recent_users = []

        for user_dict in reversed(body):
            if len(recent_users) >= number_of_unique_users:
                break

            mail_address = user_dict["email"]
            name = App.get_running_app().get_user_by_email(mail_address)
            if mail_address in ignored_addresses:
                continue
            if name in recent_users:
                continue
            else:
                recent_users.append(name)

        return recent_users

    @staticmethod
    def _is_online_database_reachable(url: str = Connections.hostname, timeout: int = 5) -> bool:
        try:
            req = requests.head(url, timeout=timeout)
            # HTTP errors are not raised by default, this statement does that
            req.raise_for_status()
            return True
        except requests.HTTPError as e:
            Logger.debug(f"StellaPayUI: Checking internet connection failed, status code {e.response.status_code}.")
        except requests.ConnectionError:
            # print("No internet connection available.")
            pass
        return False

    def _update_connection_status(self, url: str = None) -> None:
        """
        This method continuously checks whether a connection to the online database is possible. Note that this method
        should be called only once and another thread as it will block periodically.
        """
        while True:
            connection_status = DataController._is_online_database_reachable(url=url)

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

            time_until_next_check = int(
                App.get_running_app().get_config_option(
                    ConfigurationOptions.ConfigurationOption.TIME_BETWEEN_CHECKING_INTERNET_STATUS
                )
            )

            time.sleep(time_until_next_check)

    async def _update_offline_storage(self) -> None:
        """
        This method runs in a different thread and runs the updater of the offline storage periodically.
        It also makes sure to write any pending data to the backend if there is a connection
        """
        # Update JSON file with what's currently in the cache.
        self.offline_data_storage.update_file_from_cache()

        # After updating the offline storage, let's check if we can send pending data
        await self._send_pending_data_to_online_server()

    async def _send_pending_data_to_online_server(self) -> None:
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
                Logger.debug(f"StellaPayUI: Loaded pending transactions and cards")
                pending_data_json = json.load(pending_data_file)  # Load cached data into memory
            except JSONDecodeError:
                Logger.critical(f"StellaPayUI: Could not read JSON from {OfflineDataStorage.PENDING_DATA_FILE_NAME}")
                pending_data_json = None

            # If we cannot read the file, let's stop right here.
            if pending_data_json is None:
                return

            registered_pending_transactions_successfully = False

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
                    registered_pending_transactions_successfully = await self.create_transactions(shopping_cart)

                    # Check result
                    if registered_pending_transactions_successfully:
                        Logger.debug(
                            f"StellaPayUI: Registered {len(shopping_cart.basket)} new transactions from pending transactions"
                        )
                    else:
                        Logger.debug(f"StellaPayUI: Failed to register transactions from pending transactions")

                else:
                    Logger.debug(f"StellaPayUI: There were no pending transactions.")
            else:
                Logger.debug(f"StellaPayUI: There were no pending transactions.")

            # Only reset the pending data if the transactions were transmitted successfully to the backend
            if registered_pending_transactions_successfully:
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
                    success = await self.register_card_info(
                        card_id=card_id, email=card_info["email"], owner="Unknown owner"
                    )

                    if success:
                        cards_registered_successfully.append(card_id)
                    else:
                        Logger.critical(f"StellaPayUI: Could not register card '{card_id}' at server!")

            # Determine which cards were validly registered (and hence can be removed from the pending data)
            valid_cards = list(filter((lambda card: card is not None), cards_registered_successfully))

            # Remove cards that were successfully added.
            for valid_card_id in valid_cards:
                pending_data_json["cards"].pop(valid_card_id, None)

            Logger.debug(f"StellaPayUI: Registered {len(valid_cards)} cards from pending data")

            # Make sure to copy the pending data to a new JSON object so we can use it outside the 'with' statement.
            json_data_to_write = pending_data_json

        # Finally write the new JSON data to the pending data file
        with open(OfflineDataStorage.PENDING_DATA_FILE_NAME, "w") as data_file:
            json.dump(json_data_to_write, data_file, indent=4)

    # Run the setup procedure, i.e. check whether we can connect to remote server
    # If we can connect, we start authentication, otherwise we run in offline mode.
    # Make sure to run this method in a separate thread because it will be blocking.
    async def start_setup_procedure(self):

        Logger.debug(f"StellaPayUI: Waiting before setting up start procedure")
        start_time = time.perf_counter()

        await asyncio.sleep(
            int(App.get_running_app().get_config_option(ConfigurationOption.TIME_TO_WAIT_BEFORE_AUTHENTICATING)),
            loop=App.get_running_app().loop,
        )

        Logger.debug(f"StellaPayUI: Starting setup procedure after {time.perf_counter() - start_time} seconds")

        if self.running_in_online_mode():
            Logger.critical(f"StellaPayUI: Running in ONLINE mode!")
            # Start up authentication
            authentication_success = await App.get_running_app().session_manager.setup_session_async()

            if authentication_success:
                await App.get_running_app().done_loading_authentication()
            else:
                Logger.critical(f"StellaPayUI: Could not authenticate to backend!")
                sys.exit(1)
        else:
            # We need to run in offline mode. Do not run authentication to the backend (as it will fail anyway).
            Logger.critical(f"StellaPayUI: Running in OFFLINE mode!")

            await App.get_running_app().done_loading_authentication()

        time_until_we_appear_again = int(
            App.get_running_app().get_config_option(
                ConfigurationOptions.ConfigurationOption.TIME_BETWEEN_UPDATING_OFFLINE_STORAGE
            )
        )

        # Thread to keep updating the offline storage files with data from the caching manager
        while True:
            await self._update_offline_storage()
            await asyncio.sleep(time_until_we_appear_again, loop=App.get_running_app().loop)

    # Get whether we can connect to the backend or not
    def running_in_online_mode(self) -> bool:
        return self.can_use_online_database

    def register_connection_listener(self, connection_listener: ConnectionListener) -> None:
        """
        Register a listener that will be notified when a connection to the backend could be made, or was lost.
        :param connection_listener: Listener to be notified
        """
        self.on_connection_change_listeners.append(connection_listener)

import threading
from collections import OrderedDict

from kivy import Logger
from kivy.app import App

from data.DataStorage import DataStorage
from utils import Connections


class OnlineDataStorage(DataStorage):

    def __init__(self):
        self.cached_user_data: OrderedDict[str, str] = OrderedDict()

    def get_user_data(self, callback=None) -> None:

        # We're not doing any work when the result is ignored anyway.
        if callback is None:
            return

        if len(self.cached_user_data) > 0:
            Logger.debug("StellaPayUI: Using online (cached) user data")
            # Return cached user data
            callback(self.cached_user_data)
            return

        print(f"StellaPayUI: Loading user mapping on thread {threading.current_thread().name}")

        # Inner function to be able to handle callback
        def handle_data(user_data):
            nonlocal self
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

            return

        App.get_running_app().session_manager.do_get_request(url=Connections.get_users(), callback=handle_data)

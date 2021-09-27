import json
import os
import traceback
from typing import Optional

import requests
from kivy import Logger

from utils import Connections


class SessionManager:
    AUTHENTICATION_FILE = "authenticate.json"

    def __init__(self):
        self.session = None

    @staticmethod
    def parse_to_json(file):
        # Create the file if does not exist
        SessionManager.create_authentication_file()

        # The read from it.
        with open(file) as credentials:
            return json.load(credentials)

    @staticmethod
    def create_authentication_file():
        # Create the authentication file if it doesn't exist.
        if not os.path.exists(SessionManager.AUTHENTICATION_FILE):
            open(SessionManager.AUTHENTICATION_FILE, 'w').close()

    # This method authenticates to the backend and makes the session ready for use
    def setup_session(self, on_finish=None):

        self.session = requests.Session()

        self.__setup_authentication()

        # Call callback if defined
        if on_finish is not None:
            on_finish()

    def __setup_authentication(self) -> bool:
        # Convert authentication.json to json dict

        json_credentials = None

        try:
            json_credentials = self.parse_to_json(SessionManager.AUTHENTICATION_FILE)
        except Exception:
            Logger.critical(
                "StellaPayUI: You need to provide an 'authenticate.json' file for your backend credentials.")
            os._exit(1)

        response = None

        # Attempt to log in
        try:
            response = self.session.post(url=Connections.authenticate(), json=json_credentials, timeout=5)
        except Exception:
            Logger.critical(f"StellaPayUI: Something went wrong while setting up authentication to the backend server!")
            return False

        # Break control flow if the user cannot identify himself
        if response is None or (response and not response.ok):
            Logger.critical(
                "StellaPayUI: Could not correctly authenticate, error code 8. Check your username and password")
            return False
        else:
            Logger.debug("StellaPayUI: Authenticated correctly to backend.")
            return True

    # Perform a get request to the given url. You can provide a callback to receive the result.
    def do_get_request(self, url: str) -> Optional[requests.Response]:
        try:
            response = self.session.get(url, timeout=5)

            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e1:
            print("Connection was reset, so reauthenticating...")

            self.session = requests.Session()

            # Could not reauthenticate to the server
            if not self.__setup_authentication():
                return None

            Logger.critical(f"StellaPayUI: Timeout on get request {e1}")

            return self.session.get(url)
        except Exception as e2:
            Logger.critical(f"StellaPayUI: A problem with a GET request")
            traceback.print_exception(None, e2, e2.__traceback__)

            return None

    # Perform a post request to the given url. You can give do functions as callbacks (which will return the response)
    def do_post_request(self, url: str, json_data=None) -> Optional[requests.Response]:
        try:
            response = self.session.post(url, json=json_data, timeout=5)

            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e1:
            print("Connection was reset, so reauthenticating...")
            self.session = requests.Session()

            # Could not reauthenticate to the server
            if not self.__setup_authentication():
                return None

            Logger.critical(f"StellaPayUI: Timeout on post request {e1}")

            return self.session.post(url, json=json_data)
        except Exception as e2:
            Logger.critical(f"StellaPayUI: A problem with a POST request {e2}")
            return None

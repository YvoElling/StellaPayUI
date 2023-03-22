import functools
import json
import os
import sys
import threading
import traceback
from typing import Optional

import requests
from kivy import Logger
from kivy.app import App

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
            open(SessionManager.AUTHENTICATION_FILE, "w").close()

    async def setup_session_async(self) -> bool:
        self.session = requests.Session()

        return await self._setup_authentication_async()

    async def _setup_authentication_async(self) -> bool:
        json_credentials = None

        # Convert authentication.json to json dict
        try:
            json_credentials = self.parse_to_json(SessionManager.AUTHENTICATION_FILE)
        except Exception:
            Logger.critical(
                "StellaPayUI: You need to provide an 'authenticate.json' file for your backend credentials."
            )
            sys.exit(1)

        # Attempt to log in
        try:
            post_future = App.get_running_app().loop.run_in_executor(
                None, functools.partial(self.session.post, Connections.authenticate(), json=json_credentials, timeout=5)
            )
            response = await post_future
        except Exception:
            Logger.critical(f"StellaPayUI: Something went wrong while setting up authentication to the backend server!")
            return False

        # Break control flow if the user cannot identify himself
        if response is None or (response is not None and not response.ok):
            Logger.critical(
                "StellaPayUI: Could not correctly authenticate, error code 8. Check your username and password"
            )
            return False
        else:
            Logger.debug("StellaPayUI: Authenticated correctly to backend (async).")
            return True

    async def do_get_request_async(self, url: str) -> Optional[requests.Response]:
        Logger.debug(f"StellaPayUI: ({threading.current_thread().name}) Async GET request to {url}")

        if self.session is None:
            Logger.warning(f"StellaPayUI: No session was found, so initializing a session.")

            if not await self.setup_session_async():
                Logger.critical(f"StellaPayUI: Could not authenticate in new session!")
                return None

        try:
            get_future = App.get_running_app().loop.run_in_executor(
                None, functools.partial(self.session.get, url, timeout=5)
            )
            response = await get_future

            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e1:
            Logger.critical(f"StellaPayUI: Timeout on get request {e1}")
            Logger.debug("StellaPayUI: Connection was reset, trying to reauthenticate...")
            await self.setup_session_async()

            get_future = App.get_running_app().loop.run_in_executor(
                None, functools.partial(self.session.get, url, timeout=5)
            )
            response = await get_future

            return response
        except Exception as e2:
            Logger.critical(f"StellaPayUI: A problem with a GET request")
            traceback.print_exception(None, e2, e2.__traceback__)

            return None

    async def do_post_request_async(self, url: str, json_data=None) -> Optional[requests.Response]:

        Logger.debug(f"StellaPayUI: ({threading.current_thread().name}) Async POST request to {url}")
        if self.session is None:
            Logger.warning(f"StellaPayUI: No session was found, so initializing a session.")

            if not await self.setup_session_async():
                Logger.critical(f"StellaPayUI: Could not authenticate in new session!")
                return None

        try:
            post_future = App.get_running_app().loop.run_in_executor(
                None, functools.partial(self.session.post, url, timeout=5, json=json_data)
            )
            response = await post_future

            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e1:
            Logger.critical(f"StellaPayUI: Timeout on post request {e1}")
            Logger.debug("StellaPayUI: Connection was reset, trying to reauthenticate...")
            await self.setup_session_async()

            post_future = App.get_running_app().loop.run_in_executor(
                None, functools.partial(self.session.post, url, timeout=5, json=json_data)
            )
            response = await post_future

            return response
        except Exception as e2:
            Logger.critical(f"StellaPayUI: A problem with a POST request")
            traceback.print_exception(None, e2, e2.__traceback__)

            return None

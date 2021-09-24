import datetime
import os
import threading
import time
from asyncio import AbstractEventLoop
from collections import OrderedDict
from typing import Optional, Callable

import typing
from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog

from PythonNFCReader.CardListener import CardListener
from PythonNFCReader.NFCReader import CardConnectionManager
from data.OnlineDataStorage import OnlineDataStorage
from utils import Connections
from utils.Screens import Screens
from ux.SelectUserItem import SelectUserItem


class DefaultScreen(Screen):
    class NFCListener(CardListener):

        def __init__(self, default_screen: "DefaultScreen"):
            self.default_screen = default_screen

        def card_is_presented(self, uid=None) -> None:
            self.default_screen.nfc_card_presented(uid)

    def __init__(self, **kwargs):
        # Call to super (Screen class)

        super(DefaultScreen, self).__init__(**kwargs)

        self.nfc_listener = DefaultScreen.NFCListener(self)

        # Create a session to maintain cookie data for this instance
        self.event_loop: AbstractEventLoop = App.get_running_app().loop

        # Store the dialog that we use to select an active user
        self.user_select_dialog: MDDialog = None

        # Store a list of users we want to be able to select
        self.users_to_select = []

        # Add extra information to footer text
        self.ids.copyright.text = self.ids.copyright.text.replace("%year%", str(datetime.datetime.now().year)) \
            .replace("%date%", str(datetime.datetime.now().strftime("%Y/%m/%d @ %H:%M:%S")))

    def register_card_listener(self, card_connection_manager: "CardConnectionManager"):
        card_connection_manager.register_listener(self.nfc_listener)

    #
    # restarts the card listener upon reentry of the screen
    #
    def on_enter(self, *args):
        # Reset active user, because we are back at this screen.
        App.get_running_app().active_user = None
        self.ids.spinner.active = False

        # Start loading user data.
        self.event_loop.call_soon_threadsafe(self.load_user_data)

    def to_credits(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = Screens.CREDITS_SCREEN.value

    #
    # gets called when the 'NFC kaart vergeten button' is pressed
    # Shows a dialog to select a user.
    #
    def on_no_nfc(self):
        # Check if the dialog has been opened before (or whether the data has been loaded properly)
        if not self.user_select_dialog or len(self.user_select_dialog.items) < 1:
            # If not, create a dialog once.
            self.user_select_dialog = MDDialog(
                type="confirmation",
                items=self.users_to_select
            )

        # Open the dialog once it's been created.
        self.user_select_dialog.open()

    def load_user_data(self, callback: Optional[Callable] = None):
        def callback_handle(user_data: typing.Dict[str, str]):
            if user_data is not None:
                # Make sure that system can create selection dialog based on users.
                self.create_user_select_dialog(user_data)
            else:
                Logger.warning(f"StellaPayUI: Could not retrieve users!")

            # Make sure to call the original callback when we're done.
            if callback is not None:
                callback()

        # Try to grab user data
        App.get_running_app().data_controller.get_user_data(callback_handle)

    @mainthread
    def create_user_select_dialog(self, user_mapping: typing.Dict[str, str]):
        # Load usernames into user select dialog
        if len(self.users_to_select) < 1:
            for user_name, user_email in user_mapping.items():
                # store all users in a list of items that we will open with a dialog
                self.users_to_select.append(
                    SelectUserItem(user_email=user_email, callback=self.selected_active_user, text=user_name))
                # Add a callback so we know when a user has been selected

        # Create user dialog so we open it later.
        self.user_select_dialog = MDDialog(
            type="confirmation",
            items=self.users_to_select
        )

    # An active user is selected via the dialog
    def selected_active_user(self, item):
        # Close the user dialog
        self.user_select_dialog.dismiss()

        # Set member variables, these are required for making a purchase later
        user_name = item.text

        self.manager.transition = SlideTransition(direction='left')

        App.get_running_app().active_user = user_name

        # Go to the next screen
        self.manager.current = Screens.PRODUCT_SCREEN.value

    def on_leave(self, *args):
        # Hide the spinner
        self.ids.spinner.active = False

        # Dismiss the dialog if it was open
        if self.user_select_dialog:
            self.user_select_dialog.dismiss()

    def nfc_card_presented(self, uid: str):
        Logger.debug("StellaPayUI: Read NFC card with uid" + uid)

        # If we are currently making a transaction, ignore the card reading.
        if App.get_running_app().active_user is not None:
            toast("Ik negeer de gescande kaart omdat we met een transactie bezig zijn.")
            Logger.debug("StellaPayUI: Ignoring NFC card as we are currently making a transaction.")
            return

        # Show the spinner
        self.ids.spinner.active = True

        # Request user info for the specific UID to validate person
        response = App.get_running_app().session_manager.do_get_request(url=Connections.request_user_info() + uid)

        # Check response code to validate whether this user existed already. If so, proceed
        # to the productScreen, else proceed to the registerUID screen
        if response and response.ok:
            # store result in JSON
            query_json = response.json()

            # Move to WelcomeScreen
            self.manager.transition = SlideTransition(direction='left')

            # store user-mail for payment confirmation later
            user_mail = query_json["owner"]["email"]
            user_name = query_json["owner"]["name"]

            App.get_running_app().active_user = user_name

            # Go to the product screen
            self.manager.current = Screens.PRODUCT_SCREEN.value
        else:
            # User was not found, proceed to registerUID file
            self.manager.transition = SlideTransition(direction='right')
            self.manager.get_screen(Screens.REGISTER_UID_SCREEN.value).nfc_id = uid
            self.manager.current = Screens.REGISTER_UID_SCREEN.value

    def on_select_guest(self):
        self.select_special_user("Gast Account")

    def on_select_beheer(self):
        self.select_special_user("Beheer Algemeen")

    def on_select_onderhoud(self):
        self.select_special_user("Beheer Onderhoud")

    def select_special_user(self, user: str):
        # Close the user dialog
        self.user_select_dialog.dismiss()

        self.manager.transition = SlideTransition(direction='left')

        App.get_running_app().active_user = user

        # Go to the next screen
        self.manager.current = Screens.PRODUCT_SCREEN.value

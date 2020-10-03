import os
from asyncio import AbstractEventLoop
from collections import OrderedDict

from kivy import Logger
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.uix.bottomsheet import MDListBottomSheet

# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#
from PythonNFCReader.CardListener import CardListener
from PythonNFCReader.NFCReader import CardConnectionManager
from utils import Connections
from utils.Screens import Screens


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

    def register_card_listener(self, card_connection_manager: "CardConnectionManager"):
        card_connection_manager.register_listener(self.nfc_listener)

    #
    # restarts the card listener upon reentry of the screen
    #
    def on_enter(self, *args):
        # Reset active user, because we are back at this screen.
        App.get_running_app().active_user = None

        # Start loading user data.
        self.event_loop.call_soon_threadsafe(self.load_user_data)

    def to_credits(self):
        self.manager.current = Screens.CREDITS_SCREEN.value

    #
    # gets called when the 'NFC kaart vergeten button' is pressed
    # shows a bottom sheet menu with all users. The user can select himself.
    #
    def on_no_nfc(self):
        # Reset the bottom sheet because it's not working nicely
        self.bottom_sheet_menu = MDListBottomSheet()

        # Fill sheet with users
        self.fill_bottom_sheet()

        # Show the sheet
        self.bottom_sheet_menu.open()

    def load_user_data(self):

        if len(App.get_running_app().user_mapping) > 0:
            Logger.debug("Not loading user data again")
            return

        user_data = App.get_running_app().session_manager.do_get_request(url=Connections.get_users())

        Logger.debug("Loaded user data")

        App.get_running_app().user_mapping = {}

        if user_data and user_data.ok:
            # convert to json
            user_json = user_data.json()

            # append json to list and sort the list
            for user in user_json:
                # store all emails adressed in the sheet_menu
                App.get_running_app().user_mapping[user["name"]] = user["email"]

            App.get_running_app().user_mapping = OrderedDict(
                sorted(App.get_running_app().user_mapping.items(), key=lambda x: x[0]))
        else:
            Logger.critical("Error: addresses could not be fetched from server in DefaultScreen.py:on_no_nfc()")
            os._exit(1)

    def fill_bottom_sheet(self):
        for user_name, user_email in App.get_running_app().user_mapping.items():
            # store all emails addresses in the sheet_menu
            self.bottom_sheet_menu.add_item(user_name, self.selected_active_user)

    # set_mail
    def selected_active_user(self, item):
        # Set member variables, these are required for making a purchase later
        user_name = item.text

        self.manager.transition = SlideTransition(direction='left')

        App.get_running_app().active_user = user_name

        # Set the name as the name of the user on the next page
        self.manager.current = Screens.WELCOME_SCREEN.value

    def on_leave(self, *args):
        # Hide the spinner
        self.ids.spinner.active = False

    def nfc_card_presented(self, uid: str):
        Logger.debug("Read NFC card with uid" + uid)

        # If we are currently making a transaction, ignore the card reading.
        if App.get_running_app().active_user is not None:
            Logger.debug("Ignoring NFC card as we are currently making a transaction.")
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

            # Go to the welcome screen
            self.manager.current = Screens.WELCOME_SCREEN.value
        else:
            # User was not found, proceed to registerUID file
            self.manager.get_screen(Screens.REGISTER_UID_SCREEN.value).nfc_id = uid
            self.manager.current = Screens.REGISTER_UID_SCREEN.value

import os
from asyncio import AbstractEventLoop

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
from utils.Screens import Screens


class DefaultScreen(Screen):
    # Authenticate query, use local file for password/username
    authenticate = "http://staartvin.com:8181/authenticate"
    # URL for querying users and user-uid mappings
    api_url = "http://staartvin.com:8181/identification/request-user/"
    get_users_api = "http://staartvin.com:8181/users"

    class NFCListener(CardListener):

        def __init__(self, default_screen: "DefaultScreen"):
            self.default_screen = default_screen

        def card_is_presented(self, uid=None) -> None:
            self.default_screen.nfc_card_presented(uid)

    def __init__(self, **kwargs):
        # Call to super (Screen class)
        super(DefaultScreen, self).__init__(**kwargs)

        self.nfc_r = None
        self.nfc_uid = None
        self.user_mapping = {}

        self.nfc_listener = DefaultScreen.NFCListener(self)

        self.session = App.get_running_app().session

        # Keep track of whether the user is still making a transaction. If so, we ignore NFC input.
        self.making_transaction = False

        # Create a session to maintain cookie data for this instance
        self.event_loop: AbstractEventLoop = App.get_running_app().loop

    def register_card_listener(self, card_connection_manager: "CardConnectionManager"):
        card_connection_manager.register_listener(self.nfc_listener)

    #
    # restarts the card listener upon reentry of the screen
    #
    def on_enter(self, *args):
        # We are not making a transaction anymore, as we are back on this screen.
        self.making_transaction = False

        # Start loading user data.
        self.event_loop.call_soon_threadsafe(self.load_user_data)

    def to_credits(self):
        self.manager.get_screen(Screens.CREDITS_SCREEN.value).nfc_id = self.nfc_uid
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

        if len(self.user_mapping) > 0:
            Logger.debug("Not loading user data again")
            return

        user_data = self.session.get(self.get_users_api)

        Logger.debug("Loaded user data")
        self.user_mapping = {}

        if user_data.ok:
            # convert to json
            user_json = user_data.json()

            # append json to list and sort the list
            for user in user_json:
                # store all emails adressed in the sheet_menu
                self.user_mapping[user["name"]] = user["email"]
        else:
            Logger.critical("Error: addresses could not be fetched from server in DefaultScreen.py:on_no_nfc()")
            os._exit(1)

    def fill_bottom_sheet(self):
        for user_name, user_email in sorted(self.user_mapping.items()):
            # store all emails addresses in the sheet_menu
            self.bottom_sheet_menu.add_item(user_name, self.on_set_mail)

    # set_mail
    def on_set_mail(self, item):
        # Set member variables, these are required for making a purchase later
        user_name = item.text
        user_mail = self.user_mapping[user_name]

        # Set the name as the name of the user on the next page
        self.manager.get_screen(Screens.WELCOME_SCREEN.value).label.text = user_name
        self.manager.current = Screens.WELCOME_SCREEN.value

    def on_leave(self, *args):
        self.making_transaction = True

    def nfc_card_presented(self, uid: str):
        Logger.debug("Read NFC card with uid" + uid)

        # If we are currently making a transaction, ignore the card reading.
        if self.making_transaction:
            Logger.debug("Ignoring NFC card as we are currently making a transaction.")
            return

        # Send UID to Django database to validate person
        name_request = self.api_url + uid
        response = self.session.get(url=name_request)

        # Check response code to validate whether this user existed already. If so, proceed
        # to the productScreen, else proceed to the registerUID screen
        if response.ok:
            # store result in JSON
            query_json = response.json()

            # Move to WelcomeScreen
            self.manager.transition = SlideTransition(direction='left')

            # store user-mail for payment confirmation later
            self.user_mail = query_json["owner"]["email"]
            self.user_name = query_json["owner"]["name"]

            # Set the retrieved name as the name of the user on the next page
            self.manager.get_screen(Screens.WELCOME_SCREEN.value).label.text = query_json["owner"]["name"]
            self.manager.current = Screens.WELCOME_SCREEN.value
        else:
            # User was not found, proceed to registerUID file
            self.manager.get_screen(Screens.REGISTER_UID_SCREEN.value).nfc_id = uid
            self.manager.current = Screens.REGISTER_UID_SCREEN.value

import os
from asyncio import AbstractEventLoop
from collections import OrderedDict

from kivy import Logger
from kivy.app import App
from kivy.uix.screenmanager import Screen, SlideTransition
# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#
from kivymd.uix.dialog import MDDialog

from PythonNFCReader.CardListener import CardListener
from PythonNFCReader.NFCReader import CardConnectionManager
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
        self.manager.current = Screens.CREDITS_SCREEN.value

    #
    # gets called when the 'NFC kaart vergeten button' is pressed
    # Shows a dialog to select a user.
    #
    def on_no_nfc(self):
        # Check if the dialog has been opened before (or whether the data has been loaded properly)
        if not self.user_select_dialog or len(self.user_select_dialog.items) < 1:
            print("Creating dialog")
            print(f"User to select has length {len(self.users_to_select)}")
            # If not, create a dialog once.
            self.user_select_dialog = MDDialog(
                type="confirmation",
                items=self.users_to_select
            )

        # Open the dialog once it's been created.
        self.user_select_dialog.open()

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

            # Load usernames into user select dialog
            if len(self.users_to_select) < 1:
                for user_name, user_email in App.get_running_app().user_mapping.items():
                    # store all users in a list of items that we will open with a dialog
                    self.users_to_select.append(
                        SelectUserItem(user_email=user_email, callback=self.selected_active_user, text=user_name))
                    # Add a callback so we know when a user has been selected
        else:
            Logger.critical("Error: addresses could not be fetched from server")
            os._exit(1)

    # An active user is selected via the dialog
    def selected_active_user(self, item):
        # Close the user dialog
        self.user_select_dialog.dismiss()

        # Set member variables, these are required for making a purchase later
        user_name = item.text

        self.manager.transition = SlideTransition(direction='left')

        App.get_running_app().active_user = user_name

        # Set the name as the name of the user on the next page
        self.manager.current = Screens.WELCOME_SCREEN.value

    def on_leave(self, *args):
        # Hide the spinner
        self.ids.spinner.active = False

        # Dismiss the dialog if it was open
        if self.user_select_dialog:
            self.user_select_dialog.dismiss()

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

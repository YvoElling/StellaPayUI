import datetime
import functools
import time
import typing
from asyncio import AbstractEventLoop
from typing import Optional, Callable

from kivy import Logger
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog

from PythonNFCReader.CardListener import CardListener
from PythonNFCReader.NFCReader import CardConnectionManager
from data.ConnectionListener import ConnectionListener
from ds.NFCCardInfo import NFCCardInfo
from utils.Screens import Screens
from ux.SelectUserItem import SelectUserItem
from ux.UserPickerDialog import UserPickerDialog


class DefaultScreen(Screen):
    class NFCListener(CardListener):

        def __init__(self, default_screen: "DefaultScreen"):
            self.default_screen = default_screen

        def card_is_presented(self, uid=None) -> None:
            self.default_screen.nfc_card_presented(uid)

    class ConnectionChangeListener(ConnectionListener):
        # Listener that waits for input events about the change in connection status

        def __init__(self, default_screen: "DefaultScreen"):
            self.default_screen = default_screen

        def on_connection_change(self, connection_status: bool):
            # We received an event that indicates that the connection status has changed!

            current_text = self.default_screen.ids.copyright.text

            # Set new text depending on connection status
            if connection_status:
                self.default_screen.ids.copyright.text = current_text.replace("offline mode", "online mode")
            else:
                self.default_screen.ids.copyright.text = current_text.replace("online mode", "offline mode")

    def __init__(self, **kwargs):
        # Call to super (Screen class)

        super(DefaultScreen, self).__init__(**kwargs)

        self.nfc_listener = DefaultScreen.NFCListener(self)
        self.connection_change_listener = DefaultScreen.ConnectionChangeListener(self)

        # Create a session to maintain cookie data for this instance
        self.event_loop: AbstractEventLoop = App.get_running_app().loop

        # Store the dialog that we use to select an active user
        self.user_select_dialog: UserPickerDialog = None
        self.user_select_dialog_opened: bool = False

        # Store a list of users we want to be able to select
        self.users_to_select = []

        # Add extra information to footer text
        self.ids.copyright.text = self.ids.copyright.text.replace("%year%", str(datetime.datetime.now().year)) \
            .replace("%date%", str(datetime.datetime.now().strftime("%Y/%m/%d @ %H:%M:%S")))

        # Add whether we are running in offline or online mode
        self.ids.copyright.text = self.ids.copyright.text.replace("%connection_mode%",
                                                                  "online mode" if App.get_running_app().data_controller.running_in_online_mode() else "offline mode")

        # Register listener
        App.get_running_app().data_controller.register_connection_listener(self.connection_change_listener)

    def register_card_listener(self, card_connection_manager: "CardConnectionManager"):
        card_connection_manager.register_listener(self.nfc_listener)

    #
    # restarts the card listener upon reentry of the screen
    #
    def on_enter(self, *args):
        # Reset active user, because we are back at this screen.
        App.get_running_app().active_user = None
        self.ids.spinner.active = False

        self.user_select_dialog = UserPickerDialog()
        self.user_select_dialog.bind(
            selected_user=lambda _, selected_user: self.selected_active_user(selected_user))

        # Start loading user data.
        self.event_loop.call_soon_threadsafe(self.load_user_data)

    def to_credits(self):
        # Only show credits when user select dialog is not showing
        if not self.user_select_dialog_opened:
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = Screens.CREDITS_SCREEN.value

    #
    # gets called when the 'NFC kaart vergeten button' is pressed
    # Shows a dialog to select a user.
    #
    def on_no_nfc(self):
        self.user_select_dialog.show_user_selector()

        # # Open the dialog once it's been created.
        # self.user_select_dialog.open()
        # self.user_select_dialog_opened = True

    def on_user_select_dialog_close(self, event):
        self.user_select_dialog_opened = False

    def load_user_data(self, callback: Optional[Callable] = None):
        def callback_handle(user_data: typing.Dict[str, str]):
            if user_data is None:
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
                items=self.users_to_select,
                on_dismiss=self.on_user_select_dialog_close,
            )

    # An active user is selected via the dialog
    def selected_active_user(self, selected_user_name: Optional[str]):
        # Close the dialog screen
        self.user_select_dialog.close_dialog()

        # Check if a user was actually selected
        if selected_user_name is None:
            Logger.debug("StellaPayUI: No user selected!")
            return

        self.manager.transition = SlideTransition(direction='left')

        App.get_running_app().active_user = selected_user_name

        # Go to the next screen
        self.manager.current = Screens.PRODUCT_SCREEN.value

    def on_leave(self, *args):
        # Hide the spinner
        self.ids.spinner.active = False

        # Dismiss the dialog if it was open
        if self.user_select_dialog:
            self.user_select_dialog.close_dialog()

    @mainthread
    def nfc_card_presented(self, uid: str):
        Logger.debug("StellaPayUI: Read NFC card with uid" + uid)

        # If we are currently making a transaction, ignore the card reading.
        if App.get_running_app().active_user is not None:
            toast("Ik negeer de gescande kaart omdat we met een transactie bezig zijn.")
            Logger.debug("StellaPayUI: Ignoring NFC card as we are currently making a transaction.")
            return

        # Show the spinner
        self.ids.spinner.active = True

        start_time = time.time()

        # Callback to handle the card info
        def handle_card_info(card_info: NFCCardInfo):

            Logger.debug(f"StellaPayUI: Received card info in {time.time() - start_time} seconds.")

            if card_info is None:
                # User was not found, proceed to registerUID file
                self.manager.transition = SlideTransition(direction='right')
                self.manager.get_screen(Screens.REGISTER_UID_SCREEN.value).nfc_id = uid
                self.manager.current = Screens.REGISTER_UID_SCREEN.value
            else:
                # User is found
                App.get_running_app().active_user = card_info.owner_name

                # Set slide transition correctly.
                self.manager.transition = SlideTransition(direction='left')

                # Go to the product screen
                self.manager.current = Screens.PRODUCT_SCREEN.value

        # Get card info (on separate thread)
        App.get_running_app().loop.call_soon_threadsafe(
            functools.partial(App.get_running_app().data_controller.get_card_info, uid, handle_card_info))

    def on_select_guest(self):
        self.select_special_user("Gast Account")

    def on_select_beheer(self):
        self.select_special_user("Beheer Algemeen")

    def on_select_onderhoud(self):
        self.select_special_user("Beheer Onderhoud")

    def select_special_user(self, user: str):
        # Close the user dialog
        self.user_select_dialog.close_dialog()

        self.manager.transition = SlideTransition(direction='left')

        App.get_running_app().active_user = user

        # Go to the next screen
        self.manager.current = Screens.PRODUCT_SCREEN.value

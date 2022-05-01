import datetime
import functools
import json
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
from utils import Connections
from utils.Screens import Screens
from utils.SessionManager import SessionManager
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
                # Update the icon and the color of the wifi status indicator to 'online'
                self.default_screen.ids.connection_state.md_bg_color = App.get_running_app().theme_cls.green_button
                self.default_screen.ids.connection_state.icon = "wifi-strength-4"
            else:
                self.default_screen.ids.copyright.text = current_text.replace("online mode", "offline mode")
                # Update the icon and the color to 'offline'
                self.default_screen.ids.connection_state.md_bg_color = App.get_running_app().theme_cls.red_button
                self.default_screen.ids.connection_state.icon = "wifi-alert"

    def set_connectivity_icon(self, connection: bool):
        current_text = self.ids.copyright.text

        if connection:
            self.ids.copyright.text = current_text.replace("offline mode", "online mode")
            # Update the icon and the color of the wifi status indicator to 'online'
            self.ids.connection_state.md_bg_color = App.get_running_app().theme_cls.green_button
            self.ids.connection_state.icon = "wifi-strength-4"
        else:
            self.ids.copyright.text = current_text.replace("online mode", "offline mode")
            # Update the icon and the color to 'offline'
            self.ids.connection_state.md_bg_color = App.get_running_app().theme_cls.red_button
            self.ids.connection_state.icon = "wifi-alert"

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

        connection_state = App.get_running_app().data_controller.running_in_online_mode()
        self.set_connectivity_icon(connection_state)

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

    def on_pre_enter(self, *args):
        # Get today, and set time to midnight.
        today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        self.event_loop.call_soon_threadsafe(
            functools.partial(self.get_most_recent_users, today))

    def to_credits(self):
        # Only show credits when user select dialog is not showing
        if not self.user_select_dialog_opened:
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = Screens.CREDITS_SCREEN.value

    @mainthread
    def set_recent_user(self, name: str, index: int):

        if index == 0:
            self.ids.recent_user_zero.text = name
            self.ids.recent_user_zero.size_hint = (0.3, 0.075)
        elif index == 1:
            self.ids.recent_user_one.text = name
            self.ids.recent_user_one.size_hint = (0.3, 0.075)
        elif index == 2:
            self.ids.recent_user_two.text = name
            self.ids.recent_user_two.size_hint = (0.3, 0.075)

    def clear_recent_user(self, index: int):
        if index == 0:
            self.ids.recent_user_zero.text = ""
            self.ids.recent_user_zero.size_hint = (0.3, 0)
        elif index == 1:
            self.ids.recent_user_one.text = ""
            self.ids.recent_user_one.size_hint = (0.3, 0)
        elif index == 2:
            self.ids.recent_user_two.text = ""
            self.ids.recent_user_two.size_hint = (0.3, 0)

    def set_recent_users(self, names: typing.List[str]):
        if len(names) > 0:
            self.ids.title_text_recent_users.text = "[b]Of kies een recente gebruiker:[/b]"
        else:
            self.ids.title_text_recent_users.text = "Welkom! Je bent de eerste hier vandaag"

        for index, name in enumerate(names):
            self.set_recent_user(name, index)

        clear_index = min(len(names), 3)
        for i in range(clear_index, 3):
            self.clear_recent_user(i)

    def get_most_recent_users(self, today: datetime.datetime):
        response = App.get_running_app().session_manager.do_post_request(
            url=Connections.get_all_transactions(),
            json_data={
                "begin_date": today.strftime("%Y/%m/%d %H:%M:%S")
            }
        )

        if response is None or not response.ok:
            return

        try:
            body = json.loads(response.content)
        except:
            Logger.warning("StellaPayUI: Failed to parse most recent users query")
            return

        names = self.get_most_recent_names(body)
        self.set_recent_users(names)

    def get_most_recent_names(self, body: typing.List[typing.Dict]):
        ignored_addresses = ["onderhoud@solarteameindhoven.nl",
                             "beheer@solarteameindhoven.nl",
                             "info@solarteameindhoven.nl"]

        user_names = []

        for user_dict in reversed(body):
            if len(user_names) >= 3:
                break

            mail_address = user_dict["email"]
            if mail_address in ignored_addresses:
                continue
            if mail_address in user_names:
                continue
            else:
                user_names.append(
                    App.get_running_app().get_user_by_email(mail_address)
                )

        return user_names

    #
    # gets called when the 'NFC kaart vergeten button' is pressed
    # Shows a dialog to select a user.
    #
    def on_no_nfc(self):
        self.user_select_dialog.show_user_selector()

        # # Open the dialog once it's been created.
        # self.user_select_dialog.open()
        # self.user_select_dialog_opened = True

    def select_recent_user(self, obj):
        self.selected_active_user(obj)

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
        if self.user_select_dialog is not None:
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
        @mainthread
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

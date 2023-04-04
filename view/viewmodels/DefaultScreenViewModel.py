import asyncio
import threading
import time
from typing import Optional

from kivy import Logger
from kivy.app import App

from PythonNFCReader.CardListener import CardListener
from PythonNFCReader.NFCReader import CardConnectionManager
from data.ConnectionListener import ConnectionListener
from view.screens.DefaultScreen import DefaultScreen


class DefaultScreenViewModel(CardListener, ConnectionListener):
    def __init__(self, screen: DefaultScreen, card_connection_manager: CardConnectionManager):
        self.screen = screen

        # Register listener
        Logger.debug("StellaPayUI: Registering viewmodel of DefaultScreen as card listener")
        App.get_running_app().data_controller.register_connection_listener(self)
        card_connection_manager.register_listener(self)

        self.init_click_listeners()

        self.screen.bind(on_pre_enter=self.on_pre_entering_screen)

    def init_click_listeners(self):
        # Bind an event of a UI element to a method of this class or a lambda

        self.screen.ids.admin_button.ids.icon_of_button.bind(on_press=self.on_select_beheer_account)
        self.screen.ids.maintenance_button.ids.icon_of_button.bind(on_press=self.on_select_onderhoud_account)
        self.screen.ids.guest_button.ids.icon_of_button.bind(on_press=self.on_select_guest_account)

        self.screen.ids.button_select_user.bind(on_press=self.on_user_wants_to_select_purchaser)

        self.screen.ids.recent_user_zero \
            .bind(on_press=lambda _: self.user_selected_purchaser(self.screen.ids.recent_user_zero.text))
        self.screen.ids.recent_user_one \
            .bind(on_press=lambda _: self.user_selected_purchaser(self.screen.ids.recent_user_one.text))
        self.screen.ids.recent_user_two \
            .bind(on_press=lambda _: self.user_selected_purchaser(self.screen.ids.recent_user_two.text))

        self.screen.ids.icon_button.bind(on_release=lambda _: self.screen.move_to_credits_screen())

    def on_pre_entering_screen(self, *args):
        self.set_active_user(None)

        asyncio.run_coroutine_threadsafe(self.load_user_data(), loop=App.get_running_app().loop)
        asyncio.run_coroutine_threadsafe(self.get_most_recent_users(), loop=App.get_running_app().loop)

    # Fired when a NFC card is presented to the card reader
    def card_is_presented(self, uid: str) -> None:

        if uid is None:
            return

        Logger.debug(f"StellaPayUI: Read NFC card with uid '{uid}'")

        # If we are currently making a transaction, ignore the card reading.
        if App.get_running_app().active_user is not None:
            self.screen.show_toast("Ik negeer de gescande kaart omdat we met een transactie bezig zijn.")
            Logger.debug("StellaPayUI: Ignoring NFC card as we are currently making a transaction.")
            return

        self.screen.set_spinner_state(True)

        # Get card info (on separate thread)
        asyncio.run_coroutine_threadsafe(self.identify_presented_card(uid), loop=App.get_running_app().loop)

    def on_connection_change(self, connection_status: bool):
        # We received an event that indicates that the connection status has changed!
        self.screen.connection_mode = connection_status

    def set_active_user(self, user: Optional[str]):
        App.get_running_app().active_user = user

    def on_select_guest_account(self, _):
        self.user_selected_purchaser("Gast Account")

    def on_select_beheer_account(self, _):
        self.user_selected_purchaser("Beheer Algemeen")

    def on_select_onderhoud_account(self, _):
        self.user_selected_purchaser("Beheer Onderhoud")

    def on_user_wants_to_select_purchaser(self, _):
        self.screen.show_user_picker_dialog(True)
        self.screen.user_select_dialog.bind(selected_user=
                                            lambda _, selected_user: self.user_selected_purchaser(selected_user))

    def user_selected_purchaser(self, purchaser: str):
        self.set_active_user(purchaser)

        self.screen.user_selected_purchaser()

    async def load_user_data(self):
        # Try to grab user data
        user_data = await App.get_running_app().data_controller.get_user_data()

        if user_data is None:
            Logger.warning("StellaPayUI: Could not retrieve users!")

    async def get_most_recent_users(self):
        Logger.debug(f"StellaPayUI: Loading recent users on {threading.current_thread().name}")

        recent_users = await App.get_running_app().data_controller.get_recent_users(number_of_unique_users=3)

        # Update UI with most recent users
        self.screen.set_recent_users(recent_users)

    async def identify_presented_card(self, uid: str):

        Logger.debug(f"StellaPayUI: Looking up card info of '{uid}'.")

        start_time = time.time()

        card_info = await App.get_running_app().data_controller.get_card_info(uid)

        Logger.debug(f"StellaPayUI: Received card info in {time.time() - start_time} seconds.")

        if card_info is None:
            Logger.debug(f"StellaPayUI: Did not find info for card '{uid}'.")

            self.screen.move_to_register_card_screen(uid)
        else:

            if card_info.owner_name is None:
                Logger.debug(f"StellaPayUI: Card '{uid}' belongs to unknown owner.")
                return

            Logger.debug(f"StellaPayUI: Card '{uid}' belongs to {card_info.owner_name}.")

            self.user_selected_purchaser(card_info.owner_name)

import asyncio
import threading
from asyncio import AbstractEventLoop

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet

from utils.Screens import Screens


class RegisterUIDScreen(Screen):
    # APIs
    nfc_id = None

    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/RegisterUIDScreen.kv')

        # call to user with arguments
        super(RegisterUIDScreen, self).__init__(**kwargs)

        # local list that stores all mailadresses currently retrieved from the database
        self.mail_list = []

        # Timeout variables
        self.timeout_event = None
        self.timeout_time = 30

        # Create the bottom menu
        self.bottom_sheet_menu = None

        self.event_loop: AbstractEventLoop = App.get_running_app().loop

    #
    # Function is called when the product screen is entered
    #
    def on_enter(self, *args):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    #
    # Timeout callback function
    #
    def on_timeout(self, dt):
        if self.bottom_sheet_menu:
            self.bottom_sheet_menu.dismiss()
        self.timeout_event.cancel()
        self.on_cancel()

    #
    # reset timing procedure when the screen is pressed
    #
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.on_enter()

    # Return to default screen when cancelled
    @mainthread
    def on_cancel(self):
        self.manager.current = Screens.DEFAULT_SCREEN.value

    # Saves user-card-mapping to the database
    def on_save_user(self):
        # Validate whether a correct user was selected.
        if self.ids.chosen_user.text not in App.get_running_app().user_mapping.keys():
            self.ids.chosen_user.text = "Selecteer een account"
            return

        selected_user_name = self.ids.chosen_user.text
        selected_user_email = App.get_running_app().user_mapping[selected_user_name]

        asyncio.run_coroutine_threadsafe(self.register_card_mapping(selected_user_name, selected_user_email),
                                         loop=App.get_running_app().loop)

    async def register_card_mapping(self, selected_user_name, selected_user_email: str):

        card_registered = await App.get_running_app() \
            .data_controller.register_card_info(card_id=self.nfc_id, email=selected_user_email,
                                                owner=selected_user_name)

        if card_registered:
            self.card_registration_succeeded(selected_user_name)
        else:
            self.card_registration_failed(selected_user_name)

        Logger.debug(
            f"StellaPayUI: ({threading.current_thread().name}) "
            f"Registration of card '{self.nfc_id}' successful: {card_registered}")

    @mainthread
    def card_registration_succeeded(self, user: str):
        # Store the active user in the app so other screens can use it.
        App.get_running_app().active_user = user
        self.manager.current = Screens.WELCOME_SCREEN.value

    @mainthread
    def card_registration_failed(self, user: str):
        toast(
            f"Could not register this card to {user}. Try selecting your name on the home screen instead.",
            duration=5)
        self.on_cancel()

    #
    # Whenever the user wants to show the list of users to register the card to.
    #
    def on_click_user_list_button(self):
        # Restart timeout procedure
        self.timeout_event.cancel()
        self.on_enter()

        # Add items to the bottom list
        self.bottom_sheet_menu = MDListBottomSheet(height="200dp")
        for user_name, user_email in sorted(App.get_running_app().user_mapping.items()):
            # store all emails addresses in the sheet_menu
            self.bottom_sheet_menu.add_item(user_name, self.on_user_selected)
        # open the bottom sheet menu
        self.bottom_sheet_menu.open()

    # When the user selects a user to register for this card.
    def on_user_selected(self, item):
        self.timeout_event.cancel()
        self.on_enter()
        self.ids.chosen_user.text = item.text

    def on_leave(self, *args):
        # Stop the timer
        self.timeout_event.cancel()

        # Hide name of selected user
        self.ids.chosen_user.text = ""

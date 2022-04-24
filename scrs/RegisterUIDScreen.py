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

        App.get_running_app().loop.call_soon_threadsafe(
            self.register_card_mapping, selected_user_name, selected_user_email)

    def register_card_mapping(self, selected_user_name, selected_user_email: str):

        @mainthread
        def handle_card_registration(success: bool):
            Logger.debug(
                f"StellaPayUI: Received callback of new card registration on {threading.current_thread().name}")

            if success:
                # Store the active user in the app so other screens can use it.
                App.get_running_app().active_user = selected_user_name
                self.manager.current = Screens.WELCOME_SCREEN.value
            else:
                toast(
                    f"Could not register this card to {selected_user_name}. Try selecting your name on the home screen instead.",
                    duration=5)
                self.on_cancel()

        # Try to register the card.
        self.event_loop.call_soon_threadsafe(App.get_running_app().data_controller.register_card_info, self.nfc_id,
                                             selected_user_email, selected_user_name, handle_card_registration)

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


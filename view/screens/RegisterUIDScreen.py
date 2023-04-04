import asyncio
import threading

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast

from utils.Screens import Screens
from ux.UserPickerDialog import UserPickerDialog


class RegisterUIDScreen(Screen):
    # APIs
    nfc_id = None

    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file("view/layout/RegisterUIDScreen.kv")

        # call to user with arguments
        super(RegisterUIDScreen, self).__init__(**kwargs)

        # Timeout variables
        self.timeout_event = None
        self.timeout_time = 30

    #
    # Function is called when the product screen is entered
    #
    def on_enter(self, *args):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

        self.user_select_dialog = UserPickerDialog(App.get_running_app().user_mapping.keys())
        self.user_select_dialog.bind(selected_user=lambda _, selected_user: self.on_user_selected(selected_user))

    #
    # Timeout callback function
    #
    def on_timeout(self, dt):
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
        if self.user_select_dialog is not None:
            self.user_select_dialog.close_dialog()

        self.manager.current = Screens.DEFAULT_SCREEN.value

    def on_save_user(self):
        # Validate whether a correct user was selected.
        if self.ids.chosen_user.text not in App.get_running_app().user_mapping.keys():
            self.ids.chosen_user.text = "Selecteer een account"
            return

        selected_user_name = self.ids.chosen_user.text
        selected_user_email = App.get_running_app().user_mapping[selected_user_name]

        asyncio.run_coroutine_threadsafe(
            self.register_card_mapping(selected_user_name, selected_user_email), loop=App.get_running_app().loop
        )

    async def register_card_mapping(self, selected_user_name, selected_user_email: str):

        card_registered = await App.get_running_app().data_controller.register_card_info(
            card_id=self.nfc_id, email=selected_user_email, owner=selected_user_name
        )

        if card_registered:
            self.card_registration_succeeded(selected_user_name)
        else:
            self.card_registration_failed(selected_user_name)

        Logger.debug(
            f"StellaPayUI: ({threading.current_thread().name}) "
            f"Registration of card '{self.nfc_id}' successful: {card_registered}"
        )

    @mainthread
    def card_registration_succeeded(self, user: str):
        # Store the active user in the app so other screens can use it.
        App.get_running_app().active_user = user
        self.manager.current = Screens.PRODUCT_SCREEN.value

    @mainthread
    def card_registration_failed(self, user: str):
        toast(
            f"Could not register this card to {user}. Try selecting your name on the home screen instead.", duration=5
        )
        self.on_cancel()

    #
    # Whenever the user wants to show the list of users to register the card to.
    #
    def on_open_user_selector(self):  # Triggered whenever the user wants to start selecting a person
        # Restart timeout procedure
        self.timeout_event.cancel()

        self.user_select_dialog.show_user_selector()

    def on_user_selected(self, selected_user: str):  # Triggered when the user selects a person from the dialog
        self.timeout_event.cancel()
        self.ids.chosen_user.text = selected_user

        self.user_select_dialog.close_dialog()

    def on_leave(self, *args):
        # Stop the timer
        self.timeout_event.cancel()

        # Hide name of selected user
        self.ids.chosen_user.text = ""

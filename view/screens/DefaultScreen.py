import datetime
from string import Template
from typing import List, Optional

from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen, SlideTransition
from kivymd.toast import toast

from utils.Screens import Screens
from ux.UserPickerDialog import UserPickerDialog


class DefaultScreen(Screen):
    copyright_text = StringProperty("")

    connection_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        # Call to super (Screen class)
        super(DefaultScreen, self).__init__(**kwargs)

        # Store the dialog that we use to select an active user
        self.user_select_dialog: Optional[UserPickerDialog] = None

        self.copyright_text_template = Template(
            "Copyright Vincent Bolta & Yvo Elling \xa9 $year - Started this instance on $date ($connection_mode)")
        self.start_date = datetime.datetime.now()

        self.bind(connection_mode=self.on_connection_mode_changed)

    @mainthread
    def update_copyright_text(self):
        now = datetime.datetime.now()

        self.copyright_text = self.copyright_text_template.substitute(year=now.year, date=self.start_date.strftime(
            "%Y/%m/%d @ %H:%M:%S"), connection_mode="online mode" if self.connection_mode else "offline mode")

    def on_connection_mode_changed(self, _, connected: bool):

        self.update_copyright_text()

        if connected:
            # Update the icon and the color of the wifi status indicator to 'online'
            self.ids.connection_state.md_bg_color = App.get_running_app().theme_cls.green_button
            self.ids.connection_state.icon = "wifi-strength-4"
        else:
            # Update the icon and the color to 'offline'
            self.ids.connection_state.md_bg_color = App.get_running_app().theme_cls.red_button
            self.ids.connection_state.icon = "wifi-alert"

    def on_enter(self, *args):
        self.set_spinner_state(False)

    def show_user_picker_dialog(self, show: bool):
        if self.user_select_dialog is None:
            self.user_select_dialog = UserPickerDialog(App.get_running_app().user_mapping.keys())

        if show:
            self.user_select_dialog.show_user_selector()
        else:
            self.user_select_dialog.close_dialog()

    @mainthread
    def set_recent_user(self, name: str, index: int):

        if index == 0:
            recent_user_id = "recent_user_zero"
        elif index == 1:
            recent_user_id = "recent_user_one"
        elif index == 2:
            recent_user_id = "recent_user_two"
        else:
            return

        self.ids[recent_user_id].text = name
        self.ids[recent_user_id].size_hint = (0.3, 0.075)

    @mainthread
    def clear_recent_user(self, index: int):
        if index == 0:
            recent_user_id = "recent_user_zero"
        elif index == 1:
            recent_user_id = "recent_user_one"
        elif index == 2:
            recent_user_id = "recent_user_two"
        else:
            return

        self.ids[recent_user_id].text = ""
        self.ids[recent_user_id].size_hint = (0.3, 0.0)

    @mainthread
    def set_recent_users(self, names: List[str]):
        if len(names) > 0:
            self.ids.title_text_recent_users.text = "[b]Of kies een recente gebruiker:[/b]"
        else:
            self.ids.title_text_recent_users.text = "Welkom! Je bent de eerste hier vandaag"

        for index, name in enumerate(names):
            self.set_recent_user(name, index)

        clear_index = min(len(names), 3)
        for i in range(clear_index, 3):
            self.clear_recent_user(i)

    @mainthread
    # An active user is selected via the dialog
    def user_selected_purchaser(self):
        self.manager.transition = SlideTransition(direction="left")

        # Go to the next screen
        self.manager.current = Screens.PRODUCT_SCREEN.value

    def on_pre_leave(self, *args):
        # Hide the spinner
        self.set_spinner_state(False)

        # Dismiss the dialog if it was open
        if self.user_select_dialog is not None:
            self.user_select_dialog.close_dialog()

            self.user_select_dialog.clear_user_input()

    @mainthread
    def show_toast(self, message: str):
        toast(message)

    @mainthread
    def set_spinner_state(self, show: bool):
        self.ids.spinner.active = show

    @mainthread
    def move_to_register_card_screen(self, uid: str):
        # User was not found, proceed to registerUID file
        self.manager.transition = SlideTransition(direction="right")
        self.manager.get_screen(Screens.REGISTER_UID_SCREEN.value).nfc_id = uid
        self.manager.current = Screens.REGISTER_UID_SCREEN.value

    @mainthread
    def move_to_credits_screen(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = Screens.CREDITS_SCREEN.value

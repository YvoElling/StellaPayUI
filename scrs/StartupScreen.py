import sys

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

# Load KV file for this screen
from utils.Screens import Screens
from utils.async_requests.AsyncResult import AsyncResult

Builder.load_file('kvs/StartupScreen.kv')


class StartupScreen(Screen):
    users_loaded: AsyncResult = ObjectProperty()
    categories_loaded: AsyncResult = ObjectProperty()
    products_loaded: AsyncResult = ObjectProperty()

    def __init__(self, **kwargs):
        # call to user with arguments
        super(StartupScreen, self).__init__(**kwargs)

    # Calls upon entry of this screen
    #
    def on_enter(self, *args):
        App.get_running_app().loop.call_soon_threadsafe(self.check_if_all_data_is_loaded)

    # Called when all data has loaded
    def finished_loading(self, dt):
        self.manager.current = Screens.DEFAULT_SCREEN.value

    def on_users_loaded(self, _, _2):
        self.check_if_all_data_is_loaded()

    def on_categories_loaded(self, _, _2):
        self.check_if_all_data_is_loaded()

    def on_products_loaded(self, _, _2):
        self.check_if_all_data_is_loaded()

    def check_if_all_data_is_loaded(self) -> None:

        self.set_loading_text("Waiting for data to load... (0/3)")

        if self.users_loaded is None or self.users_loaded.result is None:
            Logger.debug("StellaPayUI: Waiting for users to load..")
            return
        elif self.users_loaded.received_result is False or self.users_loaded.result.data is False:
            self.set_loading_text("Failed to retrieve user data!")
            self.on_failed_to_load()
            return
        elif self.users_loaded.result.data is True:
            Logger.debug("StellaPayUI: Loaded user data!")

        self.set_loading_text("Waiting for data to load... (1/3)")

        if self.categories_loaded is None or self.categories_loaded.result is None:
            Logger.debug("StellaPayUI: Waiting for categories to load..")
            return
        elif self.categories_loaded.received_result is False or self.categories_loaded.result.data is False:
            self.set_loading_text("Failed to retrieve category data!")
            self.on_failed_to_load()
            return
        elif self.categories_loaded.result.data is True:
            Logger.debug("StellaPayUI: Loaded categories data!")

        self.set_loading_text("Waiting for data to load... (2/3)")

        if self.products_loaded is None or self.products_loaded.result is None:
            Logger.debug("StellaPayUI: Waiting for products to load..")
            return
        elif self.products_loaded.received_result is False or self.products_loaded.result.data is False:
            self.set_loading_text("Failed to retrieve products data!")
            self.on_failed_to_load()
            return
        elif self.products_loaded.result.data is True:
            Logger.debug("StellaPayUI: Loaded products data!")

        self.set_loading_text("Data has loaded!")

        self.set_loading_spinner(False)

        Clock.schedule_once(self.finished_loading, 1)

    def on_failed_to_load(self):
        self.set_loading_spinner(False)
        Clock.schedule_once(lambda: sys.exit(1), 3)

    def set_loading_spinner(self, active: bool):
        self.ids.spinner_startup.active = active

    def set_loading_text(self, text: str):
        self.ids.loading_text.text = text

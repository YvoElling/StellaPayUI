import time

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# Load KV file for this screen
from utils.Screens import Screens

Builder.load_file('kvs/StartupScreen.kv')


class StartupScreen(Screen):
    def __init__(self, **kwargs):
        # call to user with arguments
        super(StartupScreen, self).__init__(**kwargs)

        # Keep track of when data is loaded
        self.users_loaded = False
        self.categories_loaded = False
        self.products_loaded = False

    # Calls upon entry of this screen
    #
    def on_enter(self, *args):
        self.ids.loading_text.text = "Waiting for data to load..."

        App.get_running_app().loop.call_soon_threadsafe(self.wait_for_data_to_load)

    # Called when all data has loaded
    def finished_loading(self, dt):
        self.manager.current = Screens.DEFAULT_SCREEN.value

    # Called when we're waiting for the data to load
    def wait_for_data_to_load(self):
        while not self.users_loaded or not self.products_loaded or not self.categories_loaded:
            # As long as one of them is not loaded, wait for a bit
            time.sleep(0.5)

            if not self.users_loaded:
                Logger.debug("StellaPayUI: Waiting for users to load..")

            if not self.products_loaded:
                Logger.debug("StellaPayUI: Waiting for products to load..")

            if not self.categories_loaded:
                Logger.debug("StellaPayUI: Waiting for categories to load..")

        # After everything has been loaded.
        self.ids.loading_text.text = "Data has loaded!"

        # Done loading, so call callback in one second.
        Clock.schedule_once(self.finished_loading, 1)

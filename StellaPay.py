import asyncio
import subprocess
import sys
import threading
import time
from asyncio import AbstractEventLoop
from typing import Optional, Dict, Any

import kivy
from kivy import Logger
from kivy.app import App
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

import utils.ConfigurationOptions as config
from PythonNFCReader.NFCReader import CardConnectionManager
from data.DataController import DataController
from db.DatabaseManager import DatabaseManager
from ds.NFCCardInfo import NFCCardInfo
from scrs.ConfirmedScreen import ConfirmedScreen
from scrs.CreditsScreen import CreditsScreen
from scrs.DefaultScreen import DefaultScreen
from scrs.ProductScreen import ProductScreen
from scrs.ProfileScreen import ProfileScreen
from scrs.RegisterUIDScreen import RegisterUIDScreen
from scrs.StartupScreen import StartupScreen
from scrs.WelcomeScreen import WelcomeScreen
from utils import Connections
from utils.Screens import Screens
from utils.SessionManager import SessionManager

class StellaPay(MDApp):
    build_version = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.database_manager: DatabaseManager = DatabaseManager()

        # Create database and load database manager
        self.database_manager.create_static_database()
        self.database_manager.load_facts_database()

        self.card_connection_manager = CardConnectionManager()
        self.session_manager: SessionManager = SessionManager()

        # Store user that is logged in (can be none)
        self.active_user: Optional[str] = None

        # Store a mapping from user name to user email
        self.user_mapping: Dict[str, str] = {}

        # Create a data controller that is used to access data of users and products.
        self.data_controller: DataController = DataController()

        StellaPay.build_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        Logger.debug(f"StellaPayUI: Running build {self.build_version}")

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.primary_hue = "600"
        self.theme_cls.accent_pallet = "Teal"
        self.theme_cls.accent_hue = "300"
        self.theme_cls.green_button = (0.262, 0.627, 0.278, 1)
        self.theme_cls.red_button = (0.898, 0.450, 0.450, 1)
        self.theme_cls.purple_button = (0.694, 0.612, 0.851, 1)
        self.theme_cls.complementary_color_1 = (0.623, 0.858, 0.180, 1)
        self.theme_cls.complementary_color_2 = (0, 0.525, 0.490, 1)

        # Set background image to match color of STE logo
        Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

        # Define the config type (so IDE understand the type)
        self.config: ConfigParser

        configuration_option: config.ConfigurationOption
        # Set default config options (if they do not exist)
        for configuration_option in config.ConfigurationOption:
            # Create the section if it does not exist yet.
            self.config.adddefaultsection(configuration_option.section_name)
            # Set the configuration option
            self.config.setdefault(configuration_option.section_name, configuration_option.config_name,
                                   configuration_option.default_value)

        # Update config (if needed)
        self.config.write()

        # Set size of the window
        window_width = int(self.get_config_option(config.ConfigurationOption.DEVICE_WIDTH))
        window_height = int(self.get_config_option(config.ConfigurationOption.DEVICE_HEIGHT))
        Window.size = (window_width, window_height)
        Logger.info(f"StellaPayUI: Window height {window_height} and width {window_width}.")

        # Don't run in borderless mode when we're running on Linux (it doesn't seem to work so well).
        Window.borderless = False if sys.platform.startswith("linux") else True

        try:
            hostname = self.get_config_option(config.ConfigurationOption.HOSTNAME_OF_BACKEND)

            Logger.info(f"StellaPayUI: Hostname for server: {hostname}")

            Connections.hostname = hostname
        except Exception:
            Logger.warning("StellaPayUI: Using default hostname, since none was provided")
            pass

        if self.get_config_option(config.ConfigurationOption.DEVICE_SHOW_FULLSCREEN) == "True":
            Logger.info(f"StellaPayUI: Running in fullscreen mode!")
            Window.fullscreen = True
        else:
            Logger.info(f"StellaPayUI: Running in windowed mode!")
            Window.fullscreen = False

        # Show the cursor if that's requested in the config file
        Window.show_cursor = self.get_config_option(config.ConfigurationOption.DEVICE_SHOW_CURSOR) == "True"

        # Load .kv file
        Builder.load_file('kvs/DefaultScreen.kv')

        Logger.debug("StellaPayUI: Starting event loop")
        self.loop: AbstractEventLoop = asyncio.new_event_loop()
        self.event_loop_thread = threading.Thread(target=self.run_event_loop, args=(self.loop,), daemon=True)
        self.event_loop_thread.start()

        Logger.debug("StellaPayUI: Start authentication to backend")

        # Start thread that keeps track of connection status to the server.
        self.data_controller.start_connection_update_thread(Connections.connection_status())

        # Start the setup procedure in a bit
        self.loop.call_later(
            int(self.get_config_option(config.ConfigurationOption.TIME_TO_WAIT_BEFORE_AUTHENTICATING)),
            self.data_controller.start_setup_procedure)

        # Initialize defaultScreen (to create session cookies for API calls)
        ds_screen = DefaultScreen(name=Screens.DEFAULT_SCREEN.value)

        # Load screenloader and add screens
        screen_manager.add_widget(StartupScreen(name=Screens.STARTUP_SCREEN.value))
        screen_manager.add_widget(ds_screen)
        screen_manager.add_widget(WelcomeScreen(name=Screens.WELCOME_SCREEN.value))
        screen_manager.add_widget(
            RegisterUIDScreen(name=Screens.REGISTER_UID_SCREEN.value))
        screen_manager.add_widget(ConfirmedScreen(name=Screens.CONFIRMED_SCREEN.value))
        screen_manager.add_widget(CreditsScreen(name=Screens.CREDITS_SCREEN.value))
        screen_manager.add_widget(
            ProductScreen(name=Screens.PRODUCT_SCREEN.value))
        screen_manager.add_widget(ProfileScreen(name=Screens.PROFILE_SCREEN.value))

        Logger.debug("StellaPayUI: Registering default screen as card listener")
        ds_screen.register_card_listener(self.card_connection_manager)

        Logger.debug("StellaPayUI: Starting NFC reader")
        self.card_connection_manager.start_nfc_reader()

        screen_manager.get_screen(Screens.CREDITS_SCREEN.value).ids.version_build.text = str(self.build_version)

        return screen_manager

    def run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def done_loading_authentication(self):
        # The session to the server has been authenticated, so now we can start loading users and products
        # First load the users, then the categories and products

        start = time.time() * 1000

        # Callback for loaded user data
        def handle_user_data(user_data):
            if user_data is None:
                Logger.critical("StellaPayUI: Could not retrieve users from the server!")
                sys.exit(1)
                return

            Logger.info(f"StellaPayUI: Loaded {len(user_data)} users in {time.time() * 1000 - start} ms.")

            # Store the user mapping so other screens can use it.
            self.user_mapping = user_data

            screen_manager.get_screen(Screens.STARTUP_SCREEN.value).users_loaded = True

        # Load user data
        self.data_controller.get_user_data(callback=handle_user_data)

        # Callback for loaded product data
        def handle_product_data(product_data):
            Logger.info(f"StellaPayUI: Loaded {len(product_data)} products.")

            # Signal to the startup screen that the products have been loaded.
            screen_manager.get_screen(Screens.STARTUP_SCREEN.value).products_loaded = True

            self.loaded_all_users_and_products()

        # Callback for loaded category data
        def handle_category_data(category_data):
            Logger.info(f"StellaPayUI: Loaded {len(category_data)} categories.")

            # Signal to the startup screen that the categories have been loaded.
            screen_manager.get_screen(Screens.STARTUP_SCREEN.value).categories_loaded = True

            self.data_controller.get_product_data(callback=handle_product_data)

        # Get category data (and then retrieve product data)
        self.data_controller.get_category_data(callback=handle_category_data)

        # Callback to handle the card info
        def handle_card_info(card_info: NFCCardInfo):
            Logger.info(f"StellaPayUI: Loaded card info.")

        # Get card info (on separate thread)
        self.data_controller.get_card_info("test", callback=handle_card_info)

    def loaded_all_users_and_products(self):
        # This method is called whenever all users, categories and products are loaded.
        Logger.debug("StellaPayUI: Loaded all data!")

        # If we loaded everything correctly, we can tell the startup screen we loaded correctly.
        # screen_manager.get_screen(Screens.STARTUP_SCREEN.value).on_products_loaded()

    def build_config(self, config):
        config.setdefaults('device', {
            'width': '800',
            'height': '480',
            'show_cursor': 'True',
            'fullscreen': 'True'
        })

    def on_start(self):
        Logger.debug("StellaPayUI: Starting StellaPay!")

    def on_stop(self):
        Logger.debug("StellaPayUI: Stopping!")
        self.loop.stop()  # Stop event loop

    def get_git_revisions_hash(self):
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'])

    @staticmethod
    def get_app() -> "StellaPay":
        return App.get_running_app()

    def __get_config_option(self, section_name, config_option_name, default_value=None) -> Any:
        """
        Get a configuration option as defined in the *.ini file. Each config option is defined in a section, and has its
        own name. You can also provide a default value if the value is not defined.
        :param section_name: Name of the section
        :param config_option_name: Name of the config option
        :param default_value: Default value to return if the option is not defined. None by default
        :return: the value of a config option
        """

        return self.config.getdefault(section_name, config_option_name, default_value)

    def get_config_option(self, config_option: config.ConfigurationOption):
        if config_option is None:
            return None
        return self.__get_config_option(config_option.section_name, config_option.config_name,
                                        config_option.default_value)


if __name__ == '__main__':
    kivy.require('1.11.1')

    screen_manager = ScreenManager()
    StellaPay().run()

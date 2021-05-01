import asyncio
import os
import subprocess
import sys
import threading
from asyncio import AbstractEventLoop
from typing import Optional, Dict, List

import kivy
from kivy import Logger
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from PythonNFCReader.NFCReader import CardConnectionManager
from db.DatabaseManager import DatabaseManager
from ds.Product import Product
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

# os.environ['KIVY_WINDOW'] = 'egl_rpi'

kivy.require('1.11.1')

screen_manager = ScreenManager()


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

        # Store products for each category
        self.products_per_category: Dict[str, List[Product]] = {}

        # Store a mapping from user name to user email
        self.user_mapping: Dict[str, str] = {}

        StellaPay.build_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        print(f"Running build {self.build_version}")

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

        # Set size of the window
        Window.size = (int(self.config.get('device', 'width')), int(self.config.get('device', 'height')))
        Logger.info(
            f"StellaPayUI: Window height {self.config.get('device', 'height')} and width {self.config.get('device', 'width')}.")

        # Don't run in borderless mode when we're running on Linux (it doesn't seem to work so well).
        Window.borderless = False if sys.platform.startswith("linux") else True

        hostname = None

        try:
            hostname = self.config.get('server', 'hostname')

            Logger.info(f"StellaPayUI: Hostname for server: {hostname}")

            Connections.hostname = hostname
        except Exception:
            Logger.warning("StellaPayUI: Using default hostname, since none was provided")
            pass

        if self.config.get('device', 'fullscreen') == 'True':
            Logger.info(f"StellaPayUI: Running in fullscreen mode!")
            Window.fullscreen = True
        else:
            Logger.info(f"StellaPayUI: Running in windowed mode!")
            Window.fullscreen = False

        if self.config.get('device', 'show_cursor') == 'True':
            Window.show_cursor = True
        else:
            Window.show_cursor = False

        # Load .kv file
        Builder.load_file('kvs/DefaultScreen.kv')

        Logger.debug("StellaPayUI: Starting event loop")
        self.loop: AbstractEventLoop = asyncio.new_event_loop()
        self.event_loop_thread = threading.Thread(target=self.run_event_loop, args=(self.loop,), daemon=True)
        self.event_loop_thread.start()

        Logger.debug("StellaPayUI: Start authentication to backend")

        self.loop.call_soon_threadsafe(self.session_manager.setup_session, self.load_categories_and_products)

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

    def load_categories_and_products(self):
        # Get all categories names
        response = App.get_running_app().session_manager.do_get_request(url=Connections.get_categories())

        Logger.debug("StellaPayUI: Loading product categories")

        # Check status response
        if response and response.ok:

            categories = response.json()

            Logger.debug(f"StellaPayUI: Retrieved {len(categories)} categories")

            # Load tab for each category
            for cat in categories:
                # Request products from category tab_text
                request = Connections.get_products() + cat['name']
                response = App.get_running_app().session_manager.do_get_request(request)

                Logger.debug(f"StellaPayUI: Loading products for category '{cat['name']}'")

                # Evaluate server response
                if response and response.ok:
                    # convert response to json
                    products_json = response.json()

                    self.products_per_category[cat['name']] = []

                    Logger.debug(f"StellaPayUI: Retrieved {len(products_json)} products for category '{cat['name']}'")

                    # Create a product object for all
                    for product in products_json:
                        # Only add the product to the list if the product must be shown
                        if product['shown']:
                            p = Product().create_from_json(product)
                            self.products_per_category[cat['name']].append(p)
                else:
                    # Error in retrieving products from server
                    Logger.critical("StellaPayUI: Products could not be retrieved: " + response.text)
                    os._exit(1)

            # If we loaded everything correctly, we can tell the startup screen we loaded correctly.
            screen_manager.get_screen(Screens.STARTUP_SCREEN.value).on_products_loaded()
        else:
            # Error
            Logger.critical("StellaPayUI: Categories could not be retrieved: " + response.text)
            os._exit(1)

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


if __name__ == '__main__':
    StellaPay().run()

import asyncio
import json
import os
import sqlite3
import threading
from asyncio import AbstractEventLoop
from typing import Optional, Dict

import kivy
import requests
from kivy import Logger
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from PythonNFCReader.NFCReader import CardConnectionManager
from scrs.ConfirmedScreen import ConfirmedScreen
from scrs.CreditsScreen import CreditsScreen
from scrs.DefaultScreen import DefaultScreen
from scrs.ProductScreen import ProductScreen
from scrs.ProfileScreen import ProfileScreen
from scrs.RegisterUIDScreen import RegisterUIDScreen
from scrs.WelcomeScreen import WelcomeScreen
from utils.Connections import BackendURLs
from utils.Screens import Screens

kivy.require('1.11.1')

screen_manager = ScreenManager()


def create_static_database():
    # Connect to the database and return database connection object
    conn = None
    # Create all tables and add the the database file
    try:
        conn = sqlite3.connect('db/static_fun_fact_database.db')
        print(sqlite3.version)

        # # SQLite command to create table with two fields, namely product and fun_fact
        static_fun_facts_table = "CREATE TABLE IF NOT EXISTS static_fun_facts(" \
                                 "product text NOT NULL, " \
                                 "fun_fact text PRIMARY KEY " \
                                 ");"
        #
        # one_day_fun_fact_table = "CREATE TABLE IF NOT EXISTS one_day_fun_fact(" \
        #                          "product text PRIMARY KEY " \
        #                          "fun_fact text PRIMARY KEY " \
        #                          ");"
        #
        # one_week_fun_fact_table = "CREATE TABLE IF NOT EXISTS one_week_fun_fact(" \
        #                           "product text PRIMARY KEY " \
        #                           "fun_fact text PRIMARY KEY " \
        #                           ");"
        #
        # one_month_fun_fact_table = "CREATE TABLE IF NOT EXISTS one_month_fun_fact(" \
        #                            "product text PRIMARY KEY " \
        #                            "fun_fact text PRIMARY KEY " \
        #                            ");"
        #

        # Create connection to the database and add the tables
        db_conn = conn.cursor()
        db_conn.execute(static_fun_facts_table)
        # db_conn.execute(one_day_fun_fact_table)
        # db_conn.execute(one_week_fun_fact_table)
        # db_conn.execute(one_month_fun_fact_table)

    except sqlite3.Error as e:
        Logger.critical(e)
        os._exit(1)

    return conn


class StellaPay(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = create_static_database()
        self.card_connection_manager = CardConnectionManager()
        self.session = requests.Session()
        # Store user that is logged in (can be none)
        self.active_user: Optional[str] = None

        # Store a mapping from user name to user email
        self.user_mapping: Dict[str, str] = {}

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.primary_hue = "600"
        self.theme_cls.accent_pallet = "Teal"
        self.theme_cls.accent_hue = "300"
        self.theme_cls.green_button = (0.262, 0.627, 0.278, 1)
        self.theme_cls.red_button = (0.898, 0.450, 0.450, 1)
        self.theme_cls.complementary_color_1 = (0.623, 0.858, 0.180, 1)
        self.theme_cls.complementary_color_2 = (0, 0.525, 0.490, 1)

        # Set background image to match color of STE logo
        Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

        # Disable full screen (classic Python, doesn't do anything)
        Config.set('kivy', 'window_icon', 'img/StellaPayLogo.ico')
        Config.set('graphics', 'width', self.config.get('device', 'width'))
        Config.set('graphics', 'height', self.config.get('device', 'height'))

        if self.config.get('device', 'fullscreen') == 'True':
            Window.fullscreen = True
        else:
            Window.fullscreen = False

        if self.config.get('device', 'show_cursor') == 'True':
            Window.show_cursor = True
        else:
            Window.fullscreen = False

        Config.write()

        # Load .kv file
        Builder.load_file('kvs/DefaultScreen.kv')

        Logger.debug("Starting event loop")
        self.loop: AbstractEventLoop = asyncio.new_event_loop()
        self.event_loop_thread = threading.Thread(target=self.run_event_loop, args=(self.loop,), daemon=True)
        self.event_loop_thread.start()
        Logger.debug("Started event loop")

        Logger.debug("Start authentication to backend")
        self.loop.call_soon_threadsafe(self.setup_authentication)

        # Initialize defaultScreen (to create session cookies for API calls)
        ds_screen = DefaultScreen(name=Screens.DEFAULT_SCREEN.value)

        # Load screenloader and add screens
        screen_manager.add_widget(ds_screen)
        screen_manager.add_widget(WelcomeScreen(name=Screens.WELCOME_SCREEN.value))
        screen_manager.add_widget(
            RegisterUIDScreen(name=Screens.REGISTER_UID_SCREEN.value))
        screen_manager.add_widget(ConfirmedScreen(name=Screens.CONFIRMED_SCREEN.value))
        screen_manager.add_widget(CreditsScreen(name=Screens.CREDITS_SCREEN.value))
        screen_manager.add_widget(
            ProductScreen(name=Screens.PRODUCT_SCREEN.value))
        screen_manager.add_widget(ProfileScreen(name=Screens.PROFILE_SCREEN.value))

        Logger.debug("Registering default screen as card listener")
        ds_screen.register_card_listener(self.card_connection_manager)

        Logger.debug("Starting NFC reader")
        self.card_connection_manager.start_nfc_reader()

        return screen_manager

    def run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @staticmethod
    def __parse_to_json(file):
        with open(file) as credentials:
            return json.load(credentials)

    def setup_authentication(self):
        # Convert authentication.json to json dict

        json_credentials = None

        try:
            json_credentials = self.__parse_to_json('authenticate.json')
        except Exception:
            Logger.critical("You need to provide an 'authenticate.json' file for your backend credentials.")
            os._exit(1)

        # Attempt to log in
        response = self.session.post(url=BackendURLs.AUTHENTICATE.value, json=json_credentials)

        # Break control flow if the user cannot identify himself
        if not response.ok:
            Logger.critical("Could not correctly authenticate, error code 8. Check your username and password")
            os._exit(1)
        else:
            Logger.debug("Authenticated correctly to backend.")

    def build_config(self, config):
        config.setdefaults('device', {
            'width': '800',
            'height': '480',
            'show_cursor': 'True',
            'fullscreen': 'True'
        })

    def on_start(self):
        Logger.debug("Starting StellaPay!")

    def on_stop(self):
        Logger.debug("Stopping!")
        self.loop.stop()  # Stop event loop


if __name__ == '__main__':
    StellaPay().run()

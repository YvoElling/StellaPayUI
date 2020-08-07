import sqlite3

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from scrs.DefaultScreen import DefaultScreen
from scrs.WelcomeScreen import WelcomeScreen
from scrs.ConfirmedScreen import ConfirmedScreen
from scrs.CreditsScreen import CreditsScreen
from scrs.ProductScreen import ProductScreen
from scrs.ProfileScreen import ProfileScreen
from scrs.RegisterUIDScreen import RegisterUIDScreen
from kivy.core.window import Window
from kivy.config import Config

import kivy

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
        print(e)
        exit(9)

    return conn


class StellaPay(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = create_static_database()

    def build(self):
        self.theme_cls.theme_style = "Dark"

        # Set background image to match color of STE logo
        Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

        # Disable full screen (classic Python, doesn't do anything)
        Config.set('kivy', 'window_icon', 'img/StellaPayLogo.ico')
        Config.set('graphics', 'width', '800')
        Config.set('graphics', 'height', ' 480')
        # Window.show_cursor = False
        # Window.fullscreen = True
        Config.write()

        # Load .kv file
        Builder.load_file('kvs/DefaultScreen.kv')

        # Initialize defaultScreen (to create session cookies for API calls)
        ds_screen = DefaultScreen(name='DefaultScreen')
        cookies = ds_screen.get_cookies()

        # Load screenloader and add screens
        screen_manager.add_widget(ds_screen)
        screen_manager.add_widget(WelcomeScreen(name='WelcomeScreen'))
        screen_manager.add_widget(RegisterUIDScreen(name='RegisterUIDScreen', cookies=cookies))
        screen_manager.add_widget(ConfirmedScreen(name='ConfirmedScreen'))
        screen_manager.add_widget(CreditsScreen(name='CreditsScreen'))
        screen_manager.add_widget(ProductScreen(name='ProductScreen', cookies=cookies))
        screen_manager.add_widget(ProfileScreen(name='ProfileScreen'))

        screen_manager.get_screen('DefaultScreen').static_database = self.database

        return screen_manager


if __name__ == '__main__':
    StellaPay().run()

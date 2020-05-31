from kivy.app import App
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


class StellaPay(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.theme_style = "Dark"

        # Set background image to match color of STE logo
        Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

        # Disable full screen (classic Python, doesn't do anything)
        Config.set('graphics', 'width', '800')
        Config.set('graphics', 'height', ' 480')
        # Window.show_cursor = False
        # Window.fullscreen = True
        Config.write()

        # Load .kv file
        Builder.load_file('kvs/DefaultScreen.kv')

        # Initialize defaultScreen (to create session cookies for API calls)
        ds_screen = DefaultScreen(name='DefaultScreen')
        cookies =ds_screen.get_cookies()

        # Load screenloader and add screens
        screen_manager.add_widget(ds_screen)
        screen_manager.add_widget(WelcomeScreen(name='WelcomeScreen'))
        screen_manager.add_widget(RegisterUIDScreen(name='RegisterUIDScreen', cookies=cookies))
        screen_manager.add_widget(ConfirmedScreen(name='ConfirmedScreen'))
        screen_manager.add_widget(CreditsScreen(name='CreditsScreen'))
        screen_manager.add_widget(ProductScreen(name='ProductScreen', cookies=cookies))
        screen_manager.add_widget(ProfileScreen(name='ProfileScreen'))

        return screen_manager


if __name__ == '__main__':
    # run the application
    StellaPay().run()

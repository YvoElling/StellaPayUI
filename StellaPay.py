from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from scrs.DefaultScreen import DefaultScreen
from scrs.WelcomeScreen import WelcomeScreen
from scrs.ConfirmedScreen import ConfirmedScreen
from scrs.CreditsScreen import CreditsScreen
from scrs.ProductScreen import ProductScreen
from scrs.ProfileScreen import ProfileScreen
from scrs.RegisterUIDScreen import RegisterUIDScreen
from kivy.core.window import Window

import kivy
kivy.require('1.11.1')


class StellaPay(App):
    def build(self):
        return screen_manager


if __name__ == '__main__':
    # Set background image to match color of STE logo
    Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

    # Load .kv file
    Builder.load_file('kvs/screens.kv')

    # Load screenloader and add screens
    screen_manager = ScreenManager()
    screen_manager.add_widget(DefaultScreen(name='DefaultScreen'))
    screen_manager.add_widget(WelcomeScreen(name='WelcomeScreen'))
    screen_manager.add_widget(ConfirmedScreen(name='ConfirmedScreen'))
    screen_manager.add_widget(CreditsScreen(name="CreditsScreen"))
    screen_manager.add_widget(ProductScreen(name="ProductScreen"))
    screen_manager.add_widget(ProfileScreen(name="ProfileScreen"))
    screen_manager.add_widget(RegisterUIDScreen(name="RegisterUIDScreen"))

    # run the application
    StellaPay().run()

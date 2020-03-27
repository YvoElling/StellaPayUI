from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from scrs.DefaultScreen import DefaultScreen
from scrs.WelcomeScreen import WelcomeScreen
from kivy.core.window import Window

import kivy
kivy.require('1.11.1')


class StellaPay(App):
    def build(self):
        return sm


if __name__ == '__main__':
    # Set fullscreen for application
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()

    # Set background image to match color of STE logo
    Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

    #Load .kv file
    Builder.load_file('kvs/screens.kv')

    #Load screenloader and add screens
    sm = ScreenManager()
    sm.add_widget(DefaultScreen(name='DefaultScreen'))
    sm.add_widget(WelcomeScreen(name='WelcomeScreen'))

    # run the application
    StellaPay().run()

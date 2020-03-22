from kivy.app import App
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.image import *
from PythonNFCReader import NFCReader as nfc
from scrs.DefaultScreen import DefaultScreen
from kivy.core.window import Window

import kivy
kivy.require('1.11.1')


class StellaPay(App):
    def build(self):


        # img = Image(source='img/STE.png')
        # nfc_reader = nfc.NFCReader()
        return DefaultScreen()


if __name__ == '__main__':
    # Set fullscreen for application
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()

    # Set background image to match color of STE logo
    Window.clearcolor = (0.12549, 0.12549, 0.12549, 0)

    # run the application
    StellaPay().run()

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from PythonNFCReader import NFCReader as nfc
import threading

# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#


class DefaultScreen(AnchorLayout):

    def __init__(self, **kwargs):
        super(DefaultScreen, self).__init__(**kwargs)
        img = Image(source="img/STE.png")
        img.width
        self.add_widget(img)



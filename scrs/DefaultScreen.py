from kivy.uix.screenmanager import Screen
from PythonNFCReader import NFCReader as nfc
import threading


# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#
class DefaultScreen(Screen):
    uid = None
    nfc_r = None

    def __init__(self, **kwargs):
        super(DefaultScreen, self).__init__(**kwargs)

        nfc_thread = threading.Thread(target=self.create_nfc_listener)
        nfc_thread.start()

        listener_thread = threading.Thread(target=self.create_thread_listener(nfc_thread))
        listener_thread.start()

    def create_nfc_listener(self):
        self.nfc_r = nfc.NFCReader()

    def create_thread_listener(self, nfc_thread):
        nfc_thread.join()
        self.uid = self.nfc_r.get_uid()



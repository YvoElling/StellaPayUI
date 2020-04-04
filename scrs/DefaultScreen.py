from kivy.uix.screenmanager import Screen, SlideTransition
from PythonNFCReader import NFCReader as nfc
import threading
import requests


# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#
class DefaultScreen(Screen):

    def __init__(self, **kwargs):
        # Call to super (Screen class)
        super(DefaultScreen, self).__init__(**kwargs)

        # Declare member variables
        # (Apparently Python wants them here)
        self.nfc_r = None
        self.nfc_uid = None

        # Create and start a thread to listen for NFC card presentation
        nfc_thread = threading.Thread(name="NFC_reader",
                                      target=self.create_nfc_reader)
        nfc_thread.start()

        # Create and start a thread that monitors whether the nfc_thread
        # has finished. This method is chosen to avoid having a blocking
        # thread as the main UI thread
        listener_thread = threading.Thread(name="NFC_reader_monitor",
                                           target=self.launch_nfc_reader_monitor,
                                           args=(nfc_thread, ))
        listener_thread.start()

    def create_nfc_reader(self):
        # Create NFCReader() Object that waits until a card is presented
        self.nfc_r = nfc.NFCReader()

    #
    # waits for the thread @nfc_thread to finish
    # .join() is called from a seperate to avoiding a blocking main UI thread
    #
    def launch_nfc_reader_monitor(self, nfc_thread):
        # Wait for the @nfc_thread thread to finish
        nfc_thread.join()
        # get UID for presented NFC card
        self.nfc_uid = self.nfc_r.get_uid().replace(" ", "")


        # Send UID to Django database to validate person
        # placeholder
        name_request = "staartvin.com:8181/identification/request-user/" + self.nfc_uid + "/"
        response = requests.get(url=name_request)
        #print(response)

        #Move to WelcomeScreen
        self.manager.transition = SlideTransition(direction='left')
        self.manager.get_screen('WelcomeScreen').label.text = 'Vincent Bolta'
        self.manager.current = 'WelcomeScreen'

    #
    # restarts the card listener upon reentry of the screen
    #
    def restart_listeners(self):
        self.nfc_r.enable_card_listener()

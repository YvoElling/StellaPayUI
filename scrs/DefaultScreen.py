from kivy.uix.screenmanager import Screen, SlideTransition
from PythonNFCReader import NFCReader as nfc
import threading
import requests


# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#
class DefaultScreen(Screen):
    # URL for query
    api_url = "http://staartvin.com:8181/identification/request-user/"

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
        name_request = self.api_url + '12345' + '/'
        response = requests.get(url=name_request)

        # Check response code to validate whether this user existed already. If so, proceed
        # to the productScreen, else proceed to the registerUID screen
        if response.ok:
            # store result in JSON
            query_json = response.json()

            # Move to WelcomeScreen
            self.manager.transition = SlideTransition(direction='left')
            # Set the retrieved name as the name of the user on the next page
            self.manager.get_screen('WelcomeScreen').label.text = query_json["owner"]
            self.manager.current = 'WelcomeScreen'

        else:
            # User was not found, proceed to registerUID file
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'RegisterUIDScreen'

    #
    # restarts the card listener upon reentry of the screen
    #
    # def restart_listeners(self):
    #    self.nfc_r.enable_card_listener()

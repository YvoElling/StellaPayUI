import json

from kivy.uix.screenmanager import Screen, SlideTransition, NoTransition
from kivymd.uix.bottomsheet import MDListBottomSheet

from PythonNFCReader import NFCReader as nfc
import threading
import requests


# defaultScreen class
# creates the default screen when the program waits for a card to be presented
# changes when a card is presented
#
class DefaultScreen(Screen):
    # Authenticate query, use local file for password/username
    authenticate = "http://staartvin.com:8181/authenticate"
    # URL for querying users and user-uid mappings
    api_url = "http://staartvin.com:8181/identification/request-user/"
    get_users_api = "http://staartvin.com:8181/users"

    def __init__(self, **kwargs):
        # Call to super (Screen class)
        super(DefaultScreen, self).__init__(**kwargs)

        self.nfc_r = None
        self.nfc_uid = None
        self.user_mail = None
        self.user_name = None
        self.bottom_sheet_menu = None
        self.mail_dict = {}

        # Create a session to maintain cookie data for this instance
        self.requests_cookies = requests.Session()

        # Convert authentication.json to json dict
        json_credentials = self.__parse_to_json('authenticate.json')

        # Attempt to log in
        response = self.requests_cookies.post(url=self.authenticate, json=json_credentials)
        # Break control flow if the user cannot identify himself
        if not response.ok:
            print("Could not correctly authenticate, error code 8. Check your username and password")
            exit(8)

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

    # Get cookies object for other classes
    def get_cookies(self):
        return self.requests_cookies

    @staticmethod
    def __parse_to_json(file):
        with open(file) as credentials:
            return json.load(credentials)

    # Create NFCReader() Object that waits until a card is presented
    def create_nfc_reader(self):
        self.nfc_r = nfc.NFCReader()

    #
    # waits for the thread @nfc_thread to finish
    # .join() is called from a seperate to avoiding a blocking main UI thread
    #
    def launch_nfc_reader_monitor(self, nfc_thread):
        # Wait for the @nfc_thread thread to finish
        nfc_thread.join()
        # get UID for presented NFC card

        # A card could be read incorrectly, if so, restart this screen en listen for the card again
        if self.nfc_r.get_uid is None:
            self.__init__()

        self.nfc_uid = self.nfc_r.get_uid().replace(" ", "")

        # Send UID to Django database to validate person
        name_request = self.api_url + self.nfc_uid
        response = self.requests_cookies.get(url=name_request)

        # Check response code to validate whether this user existed already. If so, proceed
        # to the productScreen, else proceed to the registerUID screen
        if response.ok:
            # store result in JSON
            query_json = response.json()

            # Move to WelcomeScreen
            self.manager.transition = SlideTransition(direction='left')

            # store user-mail for payment confirmation later
            self.user_mail = query_json["owner"]["email"]
            self.user_name = query_json["owner"]["name"]

            # Set the retrieved name as the name of the user on the next page
            self.manager.get_screen('WelcomeScreen').label.text = query_json["owner"]["name"]
            self.manager.current = 'WelcomeScreen'
        else:
            # User was not found, proceed to registerUID file
            self.manager.get_screen('RegisterUIDScreen').nfc_id = self.nfc_uid
            self.manager.current = 'RegisterUIDScreen'

    #
    # restarts the card listener upon reentry of the screen
    #
    def on_enter(self, *args):
        self.__init__()

        # Disable transitions to speed up process
        self.manager.transition = NoTransition()

    def to_credits(self):
        self.manager.get_screen('CreditsScreen').nfc_id = self.nfc_uid
        self.manager.current = 'CreditsScreen'

    #
    # gets called when the 'NFC kaart vergeten button is pressed'
    # shows a bottom sheet menu with all users. The user can select himself.
    #
    def on_no_nfc(self):
        # reset bottom_sheet_menu
        self.bottom_sheet_menu = None

        # Query user data
        user_data = self.requests_cookies.get(self.get_users_api)
        mail_list = []
        self.mail_dict = {}

        if user_data.ok:
            # convert to json
            user_json = user_data.json()

            # append json to list and sort the list
            for user in user_json:
                # store all emails adressed in the sheet_menu
                self.mail_dict[user["name"]] = user["email"]
                # self.user_dict[user["name"]] = user["name"]
                mail_list.append(user["name"])
                # name_list.append(user["name"])
        else:
            print("Error: addresses could not be fetched from server in DefaultScreen.py:on_no_nfc()")
            exit(4)

        if mail_list:
            mail_list.sort()
            # Add items to the bottom list
            self.bottom_sheet_menu = MDListBottomSheet(height="200dp")
            for user in mail_list:
                # store all emails addresses in the sheet_menu
                self.bottom_sheet_menu.add_item(user, self.on_set_mail)
            # open the bottom sheet menu
            self.bottom_sheet_menu.open()

    # set_mail
    def on_set_mail(self, item):
        # Set member variables, these are required for making a purchase later
        self.user_mail = self.mail_dict[item.text]
        self.user_name = item.text

        # Set the name as the name of the user on the next page
        self.manager.get_screen('WelcomeScreen').label.text = item.text
        self.manager.current = 'WelcomeScreen'

    def on_leave(self, *args):
        self.manager.get_screen("ProductScreen").load_data(self.static_database)

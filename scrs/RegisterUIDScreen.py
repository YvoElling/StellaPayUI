from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
import requests
import re  # regex
from kivymd.uix.bottomsheet import MDListBottomSheet


class RegisterUIDScreen(Screen):
    # APIs
    get_users_api = "http://staartvin.com:8181/users"
    add_user_api = "http://staartvin.com:8181/identification/add-card-mapping"
    get_name_uid_api = "http://staartvin.com:8181/identification/request-user/"
    nfc_id = None

    def __init__(self, cookies, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/RegisterUIDScreen.kv')

        # call to user with arguments
        super(RegisterUIDScreen, self).__init__(**kwargs)

        # Retrieve cookies session so no new authentication is required
        self.requests_cookies = cookies
        self.user_json = None

        # local list that stores all mailadresses currently retrieved from the database
        self.mail_list = []

        # Timeout variables
        self.timeout_event = None
        self.timeout_time = 15

        # Create the bottom menu
        self.bottom_sheet_menu = None

        # Get all users from the database
        user_data = self.requests_cookies.get(self.get_users_api)

        if user_data.ok:
            # convert to json
            self.user_json = user_data.json()

            # append json to list and sort the list
            for user in self.user_json:
                # store all emails adressed in the sheet_menu
                self.mail_list.append(user["email"])
        else:
            print("Error: addresses could not be fetched from server")
            exit(4)

        self.mail_list.sort()

    #
    # Function is called when the product screen is entered
    #
    def on_enter(self, *args):
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    #
    # Timeout callback function
    #
    def on_timeout(self, dt):
        if self.bottom_sheet_menu:
            self.bottom_sheet_menu.dismiss()
        self.timeout_event.cancel()
        self.on_cancel()

    #
    # reset timing procedure when the screen is pressed
    #
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.on_enter()

    # Return to default screen when cancelled
    def on_cancel(self):
        self.manager.current = 'DefaultScreen'

    # Saves user-card-mapping to the database
    def on_save_user(self):
        # Validate that a user is indeed selected
        if self.ids.selected_on_mail.text == "" or self.ids.selected_on_mail.text == "Selecteer een account":
            self.ids.selected_on_mail.text = "Selecteer een account"
            return

        # Use a POST command to add connect this UID to the user
        # uid = self.manager.get_screen('DefaultScreen').nfc_uid
        pattern = '(\[b\])([a-zA-Z\.@]+)'
        filtered_mail = re.search(pattern, str(self.ids.selected_on_mail.text))
        request = self.requests_cookies.post(self.add_user_api, json={'card_id': str(self.nfc_id),
                                                         'email': str(filtered_mail.group(2))})

        # If the users was added successfully ( status_code : 200), proceed to WelcomeScreen
        if request.ok:

            # Set the name as the name of the user on the next page
            self.manager.get_screen('WelcomeScreen').label.text = self.__request_name()
            self.manager.current = 'WelcomeScreen'

        else:
            # User could not be added succesfully, give error 2.
            print("Error " + str(request.status_code) + " occurred when trying to add the user: error message: " +
                  request.text)
            exit("2")

    # Request name to go to WelcomeScreen
    def __request_name(self):
        # Prepare API request
        name_request = self.get_name_uid_api + self.nfc_id
        # Make API request
        response = self.requests_cookies.get(url=name_request)

        if response.ok:
            query_json = response.json()
            # return name of the user
            return query_json["owner"]["name"]

        else:
            # Print errorcode 3 when the user mapped to that e-mailadress does not exist, SHOULD NOT HAPPEN
            print("An error " + str(response) + ": occured when trying to access the name of the newly added account")
            exit(3)

    #
    # Select email adress from server query
    #
    def on_select_mail(self):
        # Restart timeout procedure
        self.timeout_event.cancel()
        self.on_enter()

        # Add items to the bottom list
        self.bottom_sheet_menu = MDListBottomSheet(height="200dp")
        for user in self.mail_list:
            # store all emails addresses in the sheet_menu
            self.bottom_sheet_menu.add_item(user, self.on_set_mail)
        # open the bottom sheet menu
        self.bottom_sheet_menu.open()

    def on_set_mail(self, item):
        self.ids.selected_on_mail.text = "[b]" + item.text + "[/b]"

    def on_leave(self, *args):
        self.ids.selected_on_mail.text = ""
        self.timeout_event.cancel()

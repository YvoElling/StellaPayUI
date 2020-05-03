from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
import requests


class RegisterUIDScreen(Screen):
    # APIs
    get_users_api = "http://staartvin.com:8181/users/"
    add_use_api = "http://staartvin.com:8181/identification/set-card-mapping/"

    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/RegisterUIDScreen.kv')

        # call to user with arguments
        super(RegisterUIDScreen, self).__init__(**kwargs)

        # Initialize timeout call
        self.timeout = 60
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

        # Retrieve UID from the defaultScreen
        self.uid_nfc = 5 #self.manager.get_screen('DefaultScreen').ids.nfc_uid

        # Get all users from the database
        user_data = requests.get(self.get_users_api)

        if user_data.ok :
            # Iterate over all users and add them to the dropdown list
            for user in user_data:
                self.ids.user_spinner.values.append(user['email'])

    # On add user set the text field to the selected user
    def on_spinner_select(self, text):
        self.ids.couple_name.text = text

    # Return to default screen when cancelled
    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    # Return to the DefaultScreen on timeout
    def on_timeout(self, dt):
        Clock.unschedule(self.timeout_event)
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'
        self.ids.user_spinner.is_open = False

    # Reset timeout timer when the screen is touched
    def on_touch_up(self, touch):
        Clock.unschedule(self.timeout_event)
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout)

    # Saves user-card-mapping to the database
    def on_save_user(self):
        # Store the email adress of the user
        user_mail = self.ids.couple_name.text

        # Use a POST command to add connect this UID to the user
        request = requests.post(self.add_use_api, data={user_mail: self.uid_nfc})

        # If the users was added successfully ( status_code : 200), proceed to WelcomeScreen
        if request.ok:
            self.manager.transition = SlideTransition(direction='left')

            # Set the name as the name of the user on the next page
            self.manager.get_screen('WelcomeScreen').label.text = self.request_name()
            self.manager.current = 'WelcomeScreen'

        else:
            # User could not be added succesfully, give error 2.
            print("An error occurred when trying to add the user: error code " + request.status_code)
            exit("2")

    def request_name(self):
        # Prepare API request
        name_request = self.api_url + '122345' + '/'
        # Make API request
        response = requests.get(url=name_request)

        if response.ok:
            query_json = response.json()
            # return name of the user
            return query_json["owner"]["name"]

        else:
            # Print errorcode 3 when the user mapped to that e-mailadress does not exist
            print("An error occured when trying to access the name of the newly added account")
            exit(3)

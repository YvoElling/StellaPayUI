from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
import requests


class UserDropDown(BoxLayout):
    pass


class RegisterUIDScreen(Screen):
    get_users_api = "http://staartvin.com:8181/users/"
    add_use_api = "http://staartvin.com:8181/identification/set-card-mapping/"

    def __init__(self, **kwargs):
        # Load KV file for this screen
        Builder.load_file('kvs/RegisterUIDScreen.kv')

        # call to user with arguments
        super(RegisterUIDScreen, self).__init__(**kwargs)

        # create dropdown object
        dropDownButton = UserDropDown()
        self.add_widget(dropDownButton)

        # Retrieve UID from the defaultScreen
        self.uid_nfc = 123456  #self.manager.get_screen('DefaultScreen')

        # Get all users from the database
        user_data = requests.get(self.get_users_api)

        if user_data.ok :
            # Iterate over all users and add them to the dropdown list
            for user in user_data:
                button = Button(text=user["email"])
                button.bind(on_press=self.user_selected)
                dropDownButton.dropdown.add_widget(button)
        print("Done")

    def user_selected(self, button):
        # Use a POST command to add connect this UID to the user
        request = requests.post(self.add_use_api, {button.text, self.uid_nfc})

        # If the users was added successfully ( status_code : 200), proceed to WelcomeScreen
        if request.ok:
            self.manager.transition = SlideTransition(direction='left')

            # Set the name as the name of the user on the next page
            self.manager.get_screen('WelcomeScreen').label.text = button.text
            self.manager.current = 'WelcomeScreen'

        else:
            # User could not be added succesfully, give error 2.
            print("An error occuredd when trying to add the user: error code " + request.status_code)
            exit("2")

    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog

Builder.load_file('kvs/UserPickerContent.kv')


class UserPickerContent(BoxLayout):

    def __init__(self, **kwargs):
        super(UserPickerContent, self).__init__(**kwargs)
        self.eligible_users_to_select = list(App.get_running_app().user_mapping.keys())

    def on_text_updated(self, typed_text: str):
        # Update the recycle view to only show persons that match the typed text.

        self.ids.matched_users.data = []

        user_name: str
        for user_name in self.eligible_users_to_select:
            if typed_text.lower() in user_name.lower():
                self.ids.matched_users.data.append({
                    "viewclass": "OneLineIconListItem",
                    "text": user_name,
                })


class UserPickerDialog(MDDialog):
    """
    A dialog screen that allows the user to pick a name from a list. You can open the dialog by calling show_user_selector().
    Make sure to bind to the selected_user property to be notified when the user selects some person. Note that if no person
    is selected, the property will be None.
    """

    selected_user = StringProperty(allownone=True)
    """
    Property that is updated whenever a user has been selected. You must bind to this property to be notified.
    If no person is selected, this property will be None.
    """

    def __init__(self, **kwargs):
        self.type = "custom"
        self.content_cls = UserPickerContent()
        self.title = "Select a name"

        super(UserPickerDialog, self).__init__(**kwargs)

        # Bind pressing on a button to on_user_selected function
        self.content_cls.ids.select_user_button.bind(on_release=self._on_user_selected)
        self.content_cls.ids.cancel_button.bind(on_release=self._on_cancelled_user_selection)

    # This method is called when the user presses the 'Pick user' button
    def _on_user_selected(self, _):

        most_recent_time_touched: datetime.datetime = None
        last_user_clicked: str = None

        # This is a bit of hack:
        # We loop through all shown names on the screen and search for touch events
        # We grab the name that has been touched most recently and select it as most likely candidate
        for shown_user in self.content_cls.ids.matched_users.children[0].children:
            if shown_user.last_touch is not None:
                # Convert the timestamp from UNIX timestamp to a datetime object
                time_at_touch = datetime.datetime.fromtimestamp(shown_user.last_touch.time_end)
                name_clicked = shown_user.text

                # Keep track of the most recent timestamp
                if most_recent_time_touched is None or most_recent_time_touched < time_at_touch:
                    most_recent_time_touched = time_at_touch
                    last_user_clicked = name_clicked

        # Update the property to let anyone listening know we found (or not) a user
        self.selected_user = last_user_clicked

        return True

    # This method is called whenever the user presses the 'cancel' button
    def _on_cancelled_user_selection(self, _) -> bool:
        # Update the property so listeners get notified
        self.selected_user = None
        # Close the dialog
        self.dismiss()
        return True

    def show_user_selector(self) -> None:
        """
        Open the dialog screen to allow the user to select a person.
        """
        self.open()

    def close_dialog(self) -> None:
        """
        Close the dialog
        """
        self.dismiss()

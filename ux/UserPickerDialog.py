import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog

Builder.load_file('kvs/UserPickerContent.kv')


class UserPickerContent(BoxLayout):
    picked_user = StringProperty()

    def __init__(self, **kwargs):
        super(UserPickerContent, self).__init__(**kwargs)
        self.eligible_users_to_select = list(App.get_running_app().user_mapping.keys())

        self.last_click_registered = datetime.datetime.now()

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

        # Make sure to add listeners so we get alerted whenever a child is clicked.
        for shown_user_element in self.ids.matched_users.children[0].children:
            shown_user_element.bind(on_touch_up=self.on_child_clicked)

    def on_child_clicked(self, view, touch_event):

        # Check if the user clicked this child
        if not view.collide_point(*touch_event.pos):
            return

        # For some reason the touch listener is triggered twice. We ignore any triggers that
        # are within 1 second of each other.

        now = datetime.datetime.now()
        time_since_last_click = (now - self.last_click_registered).total_seconds()

        if time_since_last_click < 1.0:
            return

        self.last_click_registered = now

        # Update the user that was picked
        self.picked_user = view.text


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

        # Listen to when a user is picked or the cancel button is pressed
        self.content_cls.bind(picked_user=self._on_user_picked)
        self.content_cls.ids.cancel_button.bind(on_release=self._on_cancelled_user_selection)

    def _on_user_picked(self, _, user: str):
        self.selected_user = user

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

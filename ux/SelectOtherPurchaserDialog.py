from typing import Optional

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, BoundedNumericProperty, BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.dialog import MDDialog

Builder.load_file("view/layout/SelectOtherPurchaserContent.kv")


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """Adds selection and focus behaviour to the view."""


class SelectableLabel(RecycleDataViewBehavior, Label):
    """Add selection support to the Label"""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Add selection on touch down"""
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        if is_selected:
            user_selected = rv.data[index]["text"]
            # Yeah, this looks dodgy (and it is!).
            # We basically call the on_user_clicked() method from the SelectOtherPurchaserContent class
            self.parent.parent.parent.on_user_clicked(user_selected)
        elif self.selected and not is_selected:
            # We deselected this item, so let them know as well!
            self.parent.parent.parent.on_user_clicked(None)

        self.selected = is_selected


# A dialog that allows the active user to select another user (and a quantity for the product)
class SelectOtherPurchaserContent(BoxLayout):
    def __init__(self, **kwargs):
        super(SelectOtherPurchaserContent, self).__init__(**kwargs)
        self.eligible_users_to_select = list(App.get_running_app().user_mapping.keys())

    def on_text_updated(self, typed_text: str):
        # Update the recycle view to only show persons that match the typed text.

        self.clear_selected_user()
        self.ids.matched_users.data = []

        user_name: str
        for user_name in self.eligible_users_to_select:
            if typed_text.lower() in user_name.lower():
                self.ids.matched_users.data.append(
                    {
                        "text": user_name,
                    }
                )

    # Fired whenever a user is clicked in the list
    # Could be None!
    def on_user_clicked(self, user_clicked: Optional[str]):
        # If a user is clicked, we want the amount in the shopping cart to be reflected in the dialog.

        # This is a way to get the dialog class (SelectOtherPurchaserDialog) from this instance
        dialog = self.parent.parent.parent
        if user_clicked is None:
            # The active selection was removed
            # Reset the selected amount to the default value because the user was deselected
            dialog.selected_amount = 1
        else:
            # We selected a new user
            from view.screens.ProductScreen import ProductScreen
            from ds.Purchase import Purchase

            # Determine how much of the selected product is already in the shopping cart
            selected_amount_of_product = ProductScreen.shopping_cart.get_amount_of_product(
                Purchase(user_clicked, dialog.product, 0)
            )

            # If it is more than zero, we adjust the number in the dialog
            if selected_amount_of_product > 0:
                dialog.selected_amount = selected_amount_of_product

    def clear_selected_user(self):
        # Make sure to set all users to 'unselected'
        self.ids.selectable_users_box.clear_selection()

    def reset_shown_users(self):
        self.clear_selected_user()
        self.ids.search_user_name_box.text = ""
        self.ids.matched_users.data = []


class SelectOtherPurchaserDialog(MDDialog):
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

    selected_amount = BoundedNumericProperty(1, min=0)
    """
    Property that reflects the selected amount of a product, set by the user. This property is adjusted whenever the user
    selects a name from the list, as it must match the value already in the shopping cart.
    """

    def __init__(self, **kwargs):
        self.type = "custom"
        self.content_cls = SelectOtherPurchaserContent()
        self.title = "Select a name"

        # For which product are we selecting a purchaser?
        self.product: Optional[str] = None

        super(SelectOtherPurchaserDialog, self).__init__(**kwargs)

        # Bind pressing on a button to on_user_selected function
        self.content_cls.ids.select_user_button.bind(on_release=self._on_pick_user_button_clicked)
        self.content_cls.ids.cancel_button.bind(on_release=self._on_cancelled_user_selection)

        self.content_cls.ids.plus.bind(on_release=self._on_plus_button_activated)
        self.content_cls.ids.minus.bind(on_release=self._on_minus_button_activated)

    # This method is called when the user presses the 'Pick user' button
    def _on_pick_user_button_clicked(self, _):

        # Loop through all users that can be selected and see if they are selected
        for shown_user in self.content_cls.ids.selectable_users_box.children:
            if shown_user.selected:  # We found a selectable user, so return it
                self.selected_user = shown_user.text
                return True

        # There is no user selected!
        self.selected_user = None

        return True

    # This method is called whenever the user presses the 'cancel' button
    def _on_cancelled_user_selection(self, _) -> bool:
        # Update the property so listeners get notified
        self.selected_user = None
        # Close the dialog
        self.dismiss()
        return True

    def _on_plus_button_activated(self, _):
        self.selected_amount += 1
        return True

    def _on_minus_button_activated(self, _):
        if self.selected_amount > 0:
            self.selected_amount -= 1
        return True

    def reset_dialog_state(self):
        self.selected_amount = 1
        self.selected_user = None
        self.content_cls.reset_shown_users()

    def show_dialog(self, product: str) -> None:
        """
        Open the dialog screen to allow the user to select a person.
        """
        # Store which product we are picking a purchaser for
        self.product = product
        # Open the dialog screen
        self.open()

    def close_dialog(self) -> None:
        """
        Close the dialog
        """
        # Reset the product that was associated with this dialog
        self.product = None
        self.dismiss()

    # Fired when the property selected_amount is changed
    def on_selected_amount(self, _, value):
        # Make sure to adjust the count text so it's reflected in the dialog
        self.content_cls.ids.count.text = str(value)

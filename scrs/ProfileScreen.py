from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu


class ProfileScreen(Screen):
    api_get_cards = "http://staartvin.com:8181/identification/cards-of-user/"
    Builder.load_file('kvs/ProfileScreen.kv')

    def __init__(self, cookies, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)

        # Store cookies for server requests
        self.cookies = cookies

        # timeout variables
        self.timeout_event = None
        self.timeout_time = 45  # Seconds

        # Datatables
        self.card_menu = None

    # Called when the screen is loaded:
    # - for retrieving user name
    def on_enter(self, *args):
        self.ids.username.text = self.manager.get_screen("DefaultScreen").user_name
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

        request = self.api_get_cards + self.manager.get_screen("DefaultScreen").user_mail
        response = self.cookies.get(url=request)

        if response.ok:
            cards_sets = response.json()
            cards = []

            # for card in cards_sets:
            #     cards.append(card["card_id"])
            #
            # self.card_menu = MDDropdownMenu(
            #     items=cards,
            #     position="center",
            #     callback=self.set_item,
            #     width_mult=4,
            # )
            #
            # self.ids.coupled_carts.add_widget(self.card_menu)

    # Return to the product page
    def on_back(self):
        self.manager.current = 'ProductScreen'
        self.timeout_event.cancel()

    # Return to defaultScreen upon timeout
    def on_timeout(self, dt):
        self.manager.current = 'DefaultScreen'

    # Reset timer when the screen is touched
    def on_touch_up(self, touch):
        self.timeout_event.cancel()
        self.timeout_event = Clock.schedule_once(self.on_timeout, self.timeout_time)

    # Clear name on leave
    def on_leave(self, *args):
        self.ids.username.text = ""
        self.manager.get_screen("ProductScreen").load_data()

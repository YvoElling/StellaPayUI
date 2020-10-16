from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# Load KV file for this screen
from utils.Screens import Screens

Builder.load_file('kvs/StartupScreen.kv')


class StartupScreen(Screen):
    def __init__(self, **kwargs):
        # call to user with arguments
        super(StartupScreen, self).__init__(**kwargs)

    # Calls upon entry of this screen
    #
    def on_enter(self, *args):
        self.ids.loading_text.text = "Loading products from database..."

    # Called by the main app when all products are loaded from the backend.
    def on_products_loaded(self):
        print("Loaded products from database.")

        self.ids.loading_text.text = "Setting up products page..."

        # Load product data
        # App.get_running_app().loop.call_soon_threadsafe(self.manager.get_screen(Screens.PRODUCT_SCREEN.value).load_category_data)
        self.manager.get_screen(Screens.PRODUCT_SCREEN.value).load_category_data()

        # self.ids.loading_text.text = "Loading user data..."
        #
        # # Load users and their data
        # # App.get_running_app().loop.call_soon_threadsafe(self.manager.get_screen(Screens.DEFAULT_SCREEN.value).load_user_data)
        # # self.manager.get_screen(Screens.DEFAULT_SCREEN.value).load_user_data()

        self.ids.loading_text.text = "Ready!"

        # Done loading, so call callback in one second.
        Clock.schedule_once(self.finished_loading, 1)

    def finished_loading(self, dt):
        print(f"Done loading in {dt} seconds")

        self.manager.current = Screens.DEFAULT_SCREEN.value

from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.tab import MDTabsBase


class TabDisplay(FloatLayout, MDTabsBase):
    pass

    #def __init__(self, text):
    #    self.timeout = 45

        # MDLabel(text="Hello")
        # Initialize parent classes
        # super(TabDisplay, self).__init__(**kwargs)

        # Load kv file
        # Builder.load_file('kvs/TabDisplay.kv')

        # Retrieve data based on text:
        # API QUERY based on text here
        # response = None #remove once API call exists
        #
        # # Evaluate query response
        # if response.ok:
        #     pass
        #
        # else:
        #     print("Data for " + text + "could not be retrieve. Validate internet connection or contact administrator")
        #     exit(5)

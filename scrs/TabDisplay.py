from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.tab import MDTabsBase

Builder.load_file('kvs/TabDisplay.kv')


class TabDisplay(FloatLayout, MDTabsBase):
    pass


from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.tab import MDTabsBase

Builder.load_file("view/layout/TabDisplay.kv")


class TabDisplay(FloatLayout, MDTabsBase):
    pass

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivymd.uix.taptargetview import MDTapTargetView


class WelcomeScreen(Screen):

    def __init__(self, **kwargs):
        Builder.load_file('kvs/WelcomeScreen.kv')
        super(WelcomeScreen, self).__init__(**kwargs)

        # connect tap-target-view
        self.tap_target_view = MDTapTargetView(
            widget=self.ids.info,
            title_text="Information",
            description_text="Version 0.1\n",
            widget_position="right_bottom"
        )

    #
    # Called when the stop button is pressed
    #
    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # Called when buy is pressed
    #
    #
    def on_buy(self):
        self.manager.get_screen('ProductScreen').user_name = self.ids.label.text
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ProductScreen'

    #
    #
    #
    def tap_target_start(self):
        if self.tap_target_view.state == "close":
            self.tap_target_view.start()
        else:
            self.tap_target_view.stop()

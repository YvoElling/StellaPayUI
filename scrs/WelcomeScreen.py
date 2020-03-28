from kivy.uix.screenmanager import Screen, SlideTransition


class WelcomeScreen(Screen):

    #
    # Called when the 'stop' button is pressed
    #
    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'

    #
    # Called when buy is pressed
    #
    #
    def on_buy(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'ProductScreen'

from kivy.uix.screenmanager import Screen, SlideTransition


class WelcomeScreen(Screen):

    #
    # Called when the 'stop' button is pressed
    #
    def on_cancel(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'DefaultScreen'
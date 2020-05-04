
from kivy.uix.button import Button


class CategoryItem(Button):

    def __init__(self, img, title, callback):
        # Call to super object
        super(CategoryItem, self).__init__()

        # Creates a button and binds the @callback function
        cat_btn = Button()
        cat_btn.bind(on_press=callback)

        # Sets the title and the image of the button
        cat_btn.text = title
        cat_btn.background_normal = img

        # Sets the size of this button
        cat_btn.size_hint = 1, 0.5
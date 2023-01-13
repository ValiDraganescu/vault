
from flet import ( ElevatedButton, colors)

class Button(ElevatedButton):

    def __init__(self, text, on_click=None):
        ElevatedButton.__init__(self, text=text, on_click=on_click)

    def set_disabled(self, disabled: bool):
        self.disabled = disabled
        if disabled:
            self.color = colors.BLUE_GREY_500
            self.bgcolor = colors.BLUE_GREY_500
        else:
            self.color = colors.WHITE
            self.bgcolor = colors.BLACK
        self.update()

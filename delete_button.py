
from flet import ( ElevatedButton, colors)

class DeleteButton(ElevatedButton):

    def __init__(self, text, on_click=None):
        ElevatedButton.__init__(self, text=text, on_click=on_click)

    def set_disabled(self, disabled: bool):
        self.disabled = disabled
        if disabled:
            self.color = colors.WHITE
            self.bgcolor = colors.RED_100
        else:
            self.color = colors.WHITE
            self.bgcolor = colors.RED_700
        self.update()

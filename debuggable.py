from flet import (
    Container,
    Page,
    colors,
    border
)

class Debuggable(Container):

    def __init__(self, page: Page, debug: bool = False):
        super().__init__()
        self.debug = debug

    def _before_build_command(self):
        super()._before_build_command()
        if self.debug:
            # set all the borders to be red and have a width of 1
            self.border = border(1, colors.RED)

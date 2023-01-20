from flet import (
    UserControl,
    Container,
    Text,
    Icon,
    Row,
    icons,
    colors,
    padding,
    FontWeight
)
from enum import Enum

class InfoPanelType(Enum):
    INFO = "info"
    WARNING = "warning"
    OKAY = "okay"
    ERROR = "error"

class InfoPanel(UserControl):

    def __init__(self, type: InfoPanelType, text):
        super().__init__()
        self.expand = True
        self.type = type
        self.text = text
        self.info_color = self.get_color()
        self.icon = self.get_icon()

    def get_icon(self):
        icon = Icon(icons.INFO, color=colors.BLUE_500)
        if self.type == InfoPanelType.WARNING:
            icon = Icon(icons.WARNING, color=colors.ORANGE_500)
        if self.type == InfoPanelType.OKAY:
            icon = Icon(icons.CHECK, color=colors.GREEN_500)
        if self.type == InfoPanelType.ERROR:
            icon = Icon(icons.ERROR, color=colors.RED_500)

        return icon

    def get_color (self):
        color = colors.BLUE_500
        if self.type == InfoPanelType.WARNING:
            color = colors.ORANGE_500
        if self.type == InfoPanelType.OKAY:
            color = colors.GREEN_500
        if self.type == InfoPanelType.ERROR:
            color = colors.RED_500

        return color

    def build(self):
        return Container(
            expand=self.expand,
            padding=padding.all(10),
            bgcolor=self.info_color,
            content=Row(
                controls=[
                    Icon(icons.INFO),
                    Text(self.text, weight=FontWeight.BOLD)
                ]
            )
        )
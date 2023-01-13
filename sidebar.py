from flet import (
    UserControl,
    Container,
    Column,
    Page,
    ListView,
    Row,
    Text,
    colors,
    TextButton,
    Icon,
    icons,
    MainAxisAlignment,
    ControlEvent,
    ElevatedButton,
    TextField,
    TextStyle
)

from logger import log
from glob import glob
from file_item import FileItem

class Sidebar(UserControl):
    SIDEBAR_WIDTH: int

    @log
    def __init__(self, page: Page, on_file_selected_listener: callable, width: int = 300):
        super().__init__()
        self.expand = True
        self.page = page
        self.SIDEBAR_WIDTH = width
        self.on_file_selected_listener = on_file_selected_listener
        self.workspace: str = None
        self.expand = True
        self.file_list_view = ListView(expand=True, spacing=5, auto_scroll=True)
        self.file_list: list[FileItem] = []

        self.add_secret_button = ElevatedButton(
            text="Add secret", on_click=self.on_add_secret)
        self.add_secret_button.visible = False

        self.search_field = TextField(
            width=self.SIDEBAR_WIDTH - 20,
            label="Search",
            color=colors.BLACK54,
            border_color=colors.BLACK54,
            focused_border_color=colors.BLACK,
            cursor_color=colors.BLACK,
            focused_color=colors.BLACK,
            selection_color=colors.BLACK,
            label_style=TextStyle(color=colors.BLACK54),
            on_change=self.on_search_change
        )
        self.search_field.visible = False

        self.sidebar_content = Container(
            expand=True,
            content=Column(
                expand=True,
                controls=[
                Row([
                    self.add_secret_button
                ]),
                Row([
                    self.search_field
                ]),
                Row(
                    controls=[
                    self.file_list_view
                ])
            ])
        )

    @log
    def did_mount(self):
        super().did_mount()

    @log
    def on_search_change(self, e: ControlEvent):
        self.reload_file_list()

    @log
    def set_workspace(self, workspace: str = None):
        self.workspace = workspace
        self.add_secret_button.visible = True
        self.search_field.visible = True
        self.read_workspace()
        self.reload_file_list()
        self.update()

    @log
    def on_add_secret(self, e: ControlEvent):
        print("add secret")

    def get_icon(self, file_type: str) -> Icon:

        file_icons = {
            "web": Icon(name=icons.WEB, color="black"),
            "app": Icon(name=icons.APPS, color="black")
        }

        return file_icons.get(file_type, Icon(name=icons.FILE_OPEN, color="black"))

    def on_file_selected(self, e: ControlEvent):
        self.on_file_selected_listener(e.control.data)

    @log
    def read_workspace(self) -> list[str]:
        self.file_list_view.controls = []
        if self.workspace is not None:
            # read the names of the documents from the workspace path
            for file_path in glob(f"{self.workspace}/*.enc"):
                self.file_list.append(FileItem(file_path))


    @log
    def is_item_displayable(self, file_item: FileItem) -> bool:
        if self.search_field.value is None:
            return True
        if self.search_field.value == "":
            return True
        return self.search_field.value in file_item.name

    @log
    def reload_file_list(self):
        for file_item in self.file_list:
            if self.is_item_displayable(file_item):
                self.file_list_view.controls.append(
                    TextButton(
                        width=self.SIDEBAR_WIDTH,
                        on_click=self.on_file_selected,
                        data=file_item.path,
                        content=Row([
                            self.get_icon(file_item.type),
                            Text(file_item.name, color="black", size=16),
                        ],
                        alignment=MainAxisAlignment.START,
                    ),
                    )
                )
        self.update()

    @log
    def build(self):

        return Container(
            content=Column(
                controls=[
                    self.sidebar_content
                ]
            ),
            width=self.SIDEBAR_WIDTH,
            bgcolor=colors.AMBER_400,
            padding=10
        )

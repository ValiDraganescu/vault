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
    def __init__(self, page: Page, on_file_selected: callable, on_create_secret: callable, width: int = 300):
        super().__init__()
        self.expand = True
        self.page = page
        self.SIDEBAR_WIDTH = width
        self.on_file_selected_listener = on_file_selected
        self.on_create_secret_listener = on_create_secret
        self.workspace: str = None

        list_view_height = self.get_list_view_height()
        self.file_list_view = self.view_list_view(list_view_height)
        self.file_list: list[FileItem] = []

        self.add_secret_button = self.view_add_secret_btn(self.on_add_secret)

        self.search_field = self.view_search_field(self.on_search_change)
        self.search_field.visible = False

        self.sidebar_content = self.view_sidbar_content(self.add_secret_button, self.search_field, self.file_list_view)

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

    @log
    def update(self):
        self.file_list_view.height = self.get_list_view_height()
        super().update()

    @log
    def did_mount(self):
        super().did_mount()

    def view_list_view(self, height: int) -> ListView:
        return ListView(expand=True, spacing=5, height=height)

    def view_add_secret_btn(self, on_click: callable) -> ElevatedButton:
        btn = ElevatedButton(text="Add secret", on_click=on_click)
        btn.visible = False
        return btn

    def view_sidbar_content(self, add_secret_btn: ElevatedButton, search_field: TextField, list_view: ListView) -> Container:
        return Container(
            expand=True,
            content=Column(
                expand=True,
                controls=[
                    Row([
                        add_secret_btn
                    ]),
                    Row([
                        search_field
                    ]),
                    Row(
                        controls=[
                            list_view
                        ])
                ])
        )

    def view_search_field(self, on_change: callable):
        return TextField(
            width=self.SIDEBAR_WIDTH - 20,
            label="Search",
            color=colors.BLACK54,
            border_color=colors.BLACK54,
            focused_border_color=colors.BLACK,
            cursor_color=colors.BLACK,
            focused_color=colors.BLACK,
            selection_color=colors.BLACK,
            label_style=TextStyle(color=colors.BLACK54),
            on_change=on_change
        )

    @log
    def on_search_change(self, e: ControlEvent):
        self.reload_file_list()

    @log
    def set_workspace(self, workspace: str = None):
        self.workspace = workspace
        self.add_secret_button.visible = True
        self.search_field.visible = True
        self.reload_workspace()
        self.update()

    def reload_workspace(self):
        self.read_workspace()
        self.reload_file_list()
        self.update()

    @log
    def on_add_secret(self, e: ControlEvent):
        self.on_create_secret_listener()

    def get_list_view_height(self) -> int:
        return self.page.height - 200

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
        self.file_list = []
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
        self.file_list_view.controls = []
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

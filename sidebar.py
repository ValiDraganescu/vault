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
    TextStyle,
    Card
)

from logger import log
from glob import glob
from events import event_bus, Events
from constants import (SIDEBAR_WIDTH)
from store import get_store
from file_viwer_content import FileViewerContent


class Sidebar(UserControl):

    
    def __init__(self, page: Page):
        super().__init__()
        self.expand = True
        self.page = page
        self.store = get_store(self.page)

        list_view_height = self.get_list_view_height()
        self.file_list_view = self.view_list_view(list_view_height)
        self.file_list: list[FileViewerContent] = []
        self.add_secret_button = self.view_add_secret_btn()
        self.add_secret_button.visible = False
        self.search_field = self.view_search_field()
        self.search_field.visible = False
        self.sidebar_content = self.view_sidbar_content()

    
    def build(self):
        return Card(
            content=Container(
                content=Column(
                    controls=[
                        self.sidebar_content
                    ]
                ),
                width=SIDEBAR_WIDTH,
                # bgcolor=colors.AMBER_400,
                padding=10
            )
        )

    
    def update(self):
        self.file_list_view.height = self.get_list_view_height()
        workspace = self.store.get_workspace()
        if workspace:
            self.add_secret_button.visible = True
            self.search_field.visible = True
            self.reload_workspace()
        super().update()

    
    def did_mount(self):
        super().did_mount()

    def view_list_view(self, height: int) -> ListView:
        return ListView(expand=True, spacing=5, height=height)

    def view_add_secret_btn(self) -> ElevatedButton:
        btn = ElevatedButton(text="Add secret", on_click=lambda _: event_bus.emit(Events.ADD_SECRET))
        return btn

    def view_sidbar_content(self) -> Container:
        return Container(
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

    def view_search_field(self):
        return TextField(
            width=SIDEBAR_WIDTH - 20,
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

    
    def on_search_change(self, e: ControlEvent):
        self.reload_file_list()
        self.update()

    def reload_workspace(self):
        self.read_workspace()
        self.reload_file_list()

    def get_list_view_height(self) -> int:
        return self.page.height - 200

    def get_icon(self, file_type: str) -> Icon:

        file_icons = {
            "web": Icon(name=icons.WEB),
            "app": Icon(name=icons.APPS)
        }

        icon = file_icons.get(file_type, Icon(name=icons.FILE_OPEN))
        return icon
    

    
    def read_workspace(self) -> list[str]:
        self.file_list = []
        workspace = self.store.get_workspace()
        if workspace is not None:
            # read the names of the documents from the workspace path
            for file_path in glob(f"{workspace}/*.enc"):
                file_name = file_path.split("/")[-1]
                self.file_list.append(FileViewerContent.from_file_name(workspace, file_name))
    
    def is_item_displayable(self, file_item: FileViewerContent) -> bool:
        if self.search_field.value is None:
            return True
        if self.search_field.value == "":
            return True
        return self.search_field.value.lower() in file_item.name.lower()

    def on_file_selected(self, e: ControlEvent):
        event_bus.emit(Events.FILE_SELECTED, e.control.data)

    
    def reload_file_list(self):
        self.file_list_view.controls = []
        for file_item in self.file_list:
            if self.is_item_displayable(file_item):
                self.file_list_view.controls.append(
                    TextButton(
                        width=SIDEBAR_WIDTH,
                        on_click=lambda e: self.on_file_selected(e),
                        data=file_item.file_path,
                        content=Row([
                            self.get_icon(file_item.type),
                            Text(file_item.name, size=16),
                        ],
                            alignment=MainAxisAlignment.START,
                        ),
                    )
                )

from flet import (
    Container,
    UserControl,
    PopupMenuItem,
    AppBar,
    Icon,
    icons,
    Text,
    colors,
    PopupMenuButton,
    margin,
    Row,
    Page,
    ElevatedButton,
    FilePicker,
    AlertDialog,
    TextButton,
    MainAxisAlignment,
    Column,
    Divider,
    TextField,
    ControlEvent,
    FilePickerResultEvent,
    SnackBar
)

from logger import log
from sidebar import Sidebar
from constants import (SIDEBAR_WIDTH)
from file_viewer import FileViewer
from events import event_bus, Events

class VaultApp(UserControl):
    page: Page
    workspace: str
    workspace_title: Text
    select_workspace_btn: ElevatedButton
    appbar_items: list[PopupMenuItem]
    appbar: AppBar
    file_picker: FilePicker
    sidebar: Sidebar
    password_input: TextField
    login_dialog: AlertDialog
    file_viewer: FileViewer

    @log
    def __init__(self, page: Page):
        super().__init__()
        self.expand = True
        self.page = page

        self.workspace = self.page.client_storage.get("workspace")
        workspace_title = self.get_wokrspace_title_text()
        self.workspace_title = self.view_workspace_title(workspace_title)
        self.select_workspace_btn = self.view_select_workspace_btn()

        self.appbar_items = self.view_appbar_items(self.on_login)
        self.appbar = self.view_appbar(
            workspace_title=self.workspace_title,
            select_workspace_btn=self.select_workspace_btn,
            appbar_items=self.appbar_items
        )
        self.page.appbar = self.appbar
        self.page.snack_bar = SnackBar(
            content=Text("")
        )
        self.page.snack_bar.open = False

        self.file_picker = self.view_file_picker(self.on_select_workspace)
        self.page.overlay.append(self.file_picker)

        self.sidebar = Sidebar(self.page)
        self.password_input = self.view_password_input()
        self.login_dialog = self.view_login_dialog(
            self.password_input, on_click=self.on_login_success)

        self.file_viewer = FileViewer(self.page)
        
        event_bus.subscribe(Events.UPDATE_SIDEBAR, self.sidebar.update)
        event_bus.subscribe(Events.ADD_SECRET, self.on_add_secret)
        event_bus.subscribe(Events.FILE_SELECTED, self.on_file_selected)

        self.update()

    @log
    def update(self):
        super().update()
        self.sidebar.update()
        # self.page.update()  

    @log
    def build(self):
        return Container(
            expand=True,
            bgcolor=colors.RED_200,
            content=Row([
                self.sidebar,
                self.file_viewer
            ])
        )

    @log
    def did_mount(self):
        super().did_mount()
        if self.workspace is not None:
            self.sidebar.set_workspace(self.workspace)

    @log
    def will_unmount(self):
        event_bus.unsubscribe(Events.UPDATE_SIDEBAR, self.sidebar.update)
        event_bus.unsubscribe(Events.ADD_SECRET, self.on_add_secret)
        event_bus.unsubscribe(Events.FILE_SELECTED, self.on_file_selected)
        return super().will_unmount()

    @log
    def on_add_secret(self):
        self.file_viewer.visible = True
        self.update()

    @log
    def on_file_selected(self, path: str):
        print("on_file_selected", path)
        self.file_viewer.visible = True
        self.file_viewer.on_file_selected(path)
        self.update()

    def view_workspace_title(self, workspace_tile: str) -> str:
        return Text(value=workspace_tile, size=16, weight="bold", color=colors.BLUE_GREY_900)

    def view_select_workspace_btn(self) -> ElevatedButton:
        return ElevatedButton(text="Select a workspace", on_click=lambda _: self.file_picker.get_directory_path())

    def view_appbar_items(self, on_login: callable):
        return [
            PopupMenuItem(text="Login", on_click=on_login),
            PopupMenuItem(),  # divider
            PopupMenuItem(text="Settings")
        ]

    def view_appbar(self, workspace_title: str, select_workspace_btn: ElevatedButton, appbar_items: list[PopupMenuItem]):
        return AppBar(
            leading=Icon(icons.SAFETY_CHECK),
            leading_width=100,
            title=Text("Git Vault", size=24, text_align="end"),
            center_title=False,
            toolbar_height=75,
            bgcolor=colors.LIGHT_BLUE_ACCENT_700,
            actions=[
                Container(
                    content=Row([
                        workspace_title,
                        select_workspace_btn
                    ]),
                ),
                Container(
                    content=PopupMenuButton(
                        items=appbar_items
                    ),
                    margin=margin.only(left=50, right=25)
                )
            ],
        )

    def view_file_picker(self, on_result: callable):
        return FilePicker(on_result=on_result)

    def view_login_dialog(self, password_input: TextField, on_click: callable):
        return AlertDialog(
            modal=True,
            title=Text("Login"),
            content=Container(
                content=Column([
                    Row([
                        Text(
                            "Please input a password, make sure it's strong and do not forget it!")
                    ]),
                    Row([Text(
                         'If you forget your password, you will not be able to recover your secrets!')]),
                    Row([Divider()]),
                    Row([password_input]),
                ])
            ),
            actions=[
                TextButton("Login", on_click=on_click),
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )

    def view_password_input(self):
        return TextField(label="Password", password=True, can_reveal_password=True)

    @log
    def on_login(self, event: ControlEvent):
        self.page.dialog = self.login_dialog
        self.login_dialog.open = True
        self.update()

    @log
    def on_login_success(self, event: ControlEvent):
        self.login_dialog.open = False
        password = self.password_input.value
        self.page.client_storage.set("password", password)
        self.update()

    @log
    def get_wokrspace_title_text(self):
        if self.workspace is None:
            return "Now workspace selected"
        else:
            return f'Workspace: {self.workspace.split("/")[-1]}'

    @log
    def on_select_workspace(self, event: FilePickerResultEvent):
        self.workspace = event.path
        self.page.client_storage.set("workspace", self.workspace)
        self.workspace_title.value = self.get_wokrspace_title_text()
        self.select_workspace_btn.text = "Change workspace"
        self.appbar.update()
        self.sidebar.set_workspace(self.workspace)
        self.update()

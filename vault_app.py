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
    FilePickerResultEvent,
    AlertDialog,
    TextButton,
    MainAxisAlignment,
    Alignment,
    Column,
    Divider,
    TextField,
    ControlEvent,
    padding
)

from logger import log
from sidebar import Sidebar

SIDEBAR_WIDTH = 300


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
    file_viewer: Container
    file_viewer_title: TextField
    file_viewer_content: TextField

    @log
    def __init__(self, page: Page):
        super().__init__()
        self.expand = True
        self.page = page
        self.workspace = None
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
        self.file_picker = self.view_file_picker(self.on_select_workspace)
        self.page.overlay.append(self.file_picker)
        self.sidebar = self.view_side_bar(self.on_file_selected_listener)
        self.password_input = self.view_password_input()
        self.login_dialog = self.view_login_dialog(self.password_input, on_click=self.on_login_success)
        self.file_viewer_title = self.view_file_viewer_title()
        self.file_viewer_content = self.view_file_viewer_content()
        self.file_viewer = self.view_file_viewer(title_text_field=self.file_viewer_title, content_text_field=self.file_viewer_content)
        self.file_viewer.visible = False
        self.page.on_resize = self.on_page_resize
        self.update()

    @log
    def update(self):
        super().update()
        self.page.update()

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
    
    def on_page_resize(self, event):
        self.file_viewer.width = self.get_file_viewer_width()
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

    def view_side_bar(self, on_file_selected_listener):
        return Sidebar(self.page, on_file_selected_listener, SIDEBAR_WIDTH)

    def view_password_input(self):
        return TextField(label="Password", password=True, can_reveal_password=True)

    def view_file_viewer_title(self):
        return TextField()

    def view_file_viewer_content(self):
        return TextField()

    def get_file_viewer_width(self):
        return self.page.width - SIDEBAR_WIDTH - 20

    def view_file_viewer(self, title_text_field: TextField = None, content_text_field: TextField = None):
        return Container(
            width=self.get_file_viewer_width(),
            height=self.page.height,
            padding=padding.all(10),
            bgcolor=colors.GREEN_200,
            alignment=Alignment(1, -1),
            content=Column(
                controls=[
                title_text_field,
                Divider(),
                content_text_field
            ])
        )

    @log
    def on_login(self, event: ControlEvent):
        self.page.dialog = self.login_dialog
        self.login_dialog.open = True
        self.update()

    @log
    def on_login_success(self, event: ControlEvent):
        self.login_dialog.open = False
        password = self.password_input.value
        self.page.session.set("password", password)
        print(password)
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
        print(self.workspace)
        self.workspace_title.value = self.get_wokrspace_title_text()
        self.select_workspace_btn.text = "Change workspace"
        self.appbar.update()
        self.sidebar.set_workspace(self.workspace)
        self.update()

    @log
    def on_file_selected_listener(self, file_path: str):
        # read file contents
        file_content = open(file_path, 'r').read()
        rows = file_content.split('\n')
        title = rows[0]
        content = '\n'.join(rows[1:])
        print(title)
        print(content)
        self.file_viewer_title.value = title
        self.file_viewer_content.value = content
        self.file_viewer.visible = True
        # decrypt file contents
        # show file contents in a new page
        self.update()

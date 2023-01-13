from flet.security import encrypt, decrypt
from flet import (
    Container,
    UserControl,
    PopupMenuItem,
    AppBar,
    Icon,
    icons,
    IconButton,
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
    TextStyle,
    padding,
    Alignment,
    ControlEvent,
    FilePickerResultEvent,
    SnackBar,
    Dropdown,
    dropdown,
    Card
)

from logger import log
from sidebar import Sidebar
from button import Button
from delete_button import DeleteButton
from pyperclip import (copy)
from file_type import FileType, FILE_TYPE_VALUES
from os import remove

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

        self.sidebar = self.view_side_bar(
            self.on_file_selected, self.on_create_secret)
        self.password_input = self.view_password_input()
        self.login_dialog = self.view_login_dialog(
            self.password_input, on_click=self.on_login_success)

        self.file_viewer_copy_title_btn = self.view_copy_title_btn()
        self.file_viewer_copy_content_btn = self.view_copy_content_btn()
        self.file_viewer_title = self.view_file_viewer_title()
        self.file_viewer_content = self.view_file_viewer_content()
        self.file_viewer_save_btn = self.view_save_file_btn(
            self.on_file_save_click)
        self.file_viewer_edit_btn = self.view_edit_file_btn(
            self.on_file_edit_click
        )
        self.file_viewer_delete_btn = self.view_delete_file_btn(
            self.on_file_delete_click
        )
        self.file_viewer_file_type_picker = self.view_file_viewer_file_type_picker()
        self.file_viewer = self.view_file_viewer()
        self.file_viewer.visible = False
        self.page.on_resize = self.on_page_resize
        self.update()

    @log
    def update(self):
        super().update()
        self.sidebar.update()
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

    @log
    def did_mount(self):
        super().did_mount()
        if self.workspace is not None:
            self.sidebar.set_workspace(self.workspace)

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

    def view_side_bar(self, on_file_selected, on_create_secret):
        return Sidebar(self.page, on_file_selected, on_create_secret, SIDEBAR_WIDTH)

    def view_password_input(self):
        return TextField(label="Password", password=True, can_reveal_password=True)

    def view_save_file_btn(self, on_click: callable):
        btn = Button(text="Save", on_click=on_click)
        return btn

    @log
    def on_file_save_click(self, event):
        title = self.file_viewer_title.value
        content = self.file_viewer_content.value
        type = self.file_viewer_file_type_picker.value
        password = self.page.client_storage.get("password")

        if password is None:
            self.page.snack_bar.content = Text("You do not have a password set, please login first!")
            self.page.snack_bar.open = True
            self.update()
            return

        if title == "" or content == "":
            return

        self.file_viewer_edit_btn.set_disabled(False)
        self.file_viewer_save_btn.set_disabled(True)
        self.file_viewer_title.disabled = True
        self.file_viewer_content.disabled = True
        
        print(f"Saving file {title}, {content}\n with type {type}")
        file_name = f'{type}#{title.replace(" ", "_")}'
        file = open(f'{self.workspace}/{file_name}.enc', "w")
        
        encrypted_content = encrypt(f'{title}\n{content}', password)
        file.write(encrypted_content)
        file.close()
        self.sidebar.reload_workspace()
        self.update()

    def view_edit_file_btn(self, on_click: callable):
        btn = Button(text="Edit", on_click=on_click)
        return btn

    def view_delete_file_btn(self, on_click: callable):
        btn = DeleteButton(text="Delete", on_click=on_click, )
        return btn
    
    def on_file_delete_click(self, event):
        title = self.file_viewer_title.value
        type = self.file_viewer_file_type_picker.value
        file_name = f'{type}#{title.replace(" ", "_")}'
        file_path = f'{self.workspace}/{file_name}.enc'
        remove(file_path)
        self.sidebar.reload_workspace()
        self.update()


    @log
    def on_file_edit_click(self, event):
        self.file_viewer_edit_btn.set_disabled(True)
        self.file_viewer_save_btn.set_disabled(False)
        self.file_viewer_title.disabled = False
        self.file_viewer_content.disabled = False
        self.update()

    @log
    def copy_to_clipboard(self, text):
        copy(text)
        self.page.snack_bar.content = Text("Copied to clipboard")
        self.page.snack_bar.open = True
        self.update()

    # on click it copies the file_viewer_title text to cplipboard
    def view_copy_title_btn(self):
        return Container(
            content=IconButton(
                icon=icons.COPY,
                on_click=lambda _: self.copy_to_clipboard(
                    self.file_viewer_title.value),
            )
        )

    def view_copy_content_btn(self):

        return Container(
            content=IconButton(
                icon=icons.COPY,
                on_click=lambda _: self.copy_to_clipboard(
                    self.file_viewer_content.value)
            )
        )

    def view_file_viewer_title(self):
        return TextField(
            expand=True,
            label="Title",
            label_style=TextStyle(size=16, weight="bold"),
        )

    def view_file_viewer_content(self):
        return TextField(
            expand=True,
            multiline=True,
            label="Content",
            label_style=TextStyle(size=16, weight="bold"),
        )

    def on_file_picker_change(self, event):
        print(self.file_viewer_file_type_picker.value)
        self.update()

    def view_file_viewer_file_type_picker(self):
        options = []

        for file_type in FileType:
            option = dropdown.Option(
                text=FILE_TYPE_VALUES[file_type], key=file_type.value)
            options.append(option)

        file_type_picker = Dropdown(
            width=200,
            options=options
        )
        return file_type_picker

    def get_file_viewer_width(self):
        return self.page.width - SIDEBAR_WIDTH - 20

    def view_file_viewer(self):
        return Card(
            width=self.get_file_viewer_width(),
            height=self.page.height,
            content=Container(
                padding=padding.all(10),
                alignment=Alignment(1, -1),
                content=Column(
                    controls=[
                        Row(
                            alignment=MainAxisAlignment.END,
                            controls=[
                                self.file_viewer_edit_btn,
                                self.file_viewer_save_btn,
                                self.file_viewer_delete_btn
                            ]),
                        Row([self.file_viewer_file_type_picker]),
                        Divider(),
                        Row([self.file_viewer_title,
                            self.file_viewer_copy_title_btn]),
                        Divider(),
                        Row([self.file_viewer_content,
                            self.file_viewer_copy_content_btn])
                    ])
            )
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

    @log
    def on_file_selected(self, file_path: str):
        # read file contents
        file_content = open(file_path, 'r').read()
        password = self.page.client_storage.get("password")
        decrypted_content = decrypt(file_content, password)
        file_name = file_path.split("/")[-1]
        file_type = file_name.split("#")[0]
        rows = decrypted_content.split('\n')
        title = rows[0]
        content = '\n'.join(rows[1:])
        print(title)
        print(content)
        self.file_viewer_title.value = title
        self.file_viewer_content.value = content
        self.file_viewer.visible = True
        self.file_viewer_edit_btn.set_disabled(False)
        self.file_viewer_save_btn.set_disabled(True)
        self.file_viewer_delete_btn.set_disabled(False)
        self.file_viewer_title.disabled = True
        self.file_viewer_content.disabled = True
        self.file_viewer_file_type_picker.value = file_type
        # decrypt file contents
        # show file contents in a new page
        self.update()

    @log
    def on_create_secret(self):
        self.file_viewer_title.value = ""
        self.file_viewer_content.value = ""
        self.file_viewer.visible = True
        self.file_viewer_edit_btn.set_disabled(True)
        self.file_viewer_delete_btn.set_disabled(True)
        self.file_viewer_save_btn.set_disabled(False)
        self.file_viewer_title.disabled = False
        self.file_viewer_content.disabled = False
        self.update()

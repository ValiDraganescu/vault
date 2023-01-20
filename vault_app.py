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
    TextField,
    ControlEvent,
    FilePickerResultEvent,
    SnackBar
)

from logger import log
from sidebar import Sidebar
from constants import (SIDEBAR_WIDTH)
from file_viewer import FileViewer
from file_type import FileType
from events import event_bus, Events
from store import get_store
from dialog.login_dialog import LoginDialog
from security_manager import SecurityManager
from file_viwer_content import FileViewerContent
import csv

class VaultApp(UserControl):
    page: Page
    workspace_title: Text
    select_workspace_btn: ElevatedButton
    appbar_items: list[PopupMenuItem]
    appbar: AppBar
    file_picker: FilePicker
    sidebar: Sidebar
    password_input: TextField
    login_dialog: AlertDialog
    file_viewer: FileViewer

    
    def __init__(self, page: Page):
        super().__init__()
        self.expand = True
        self.page = page
        self.store = get_store(self.page)
        self.security = SecurityManager()

        private_key = self.store.get_private_key()

        self.select_workspace_btn = self.view_select_workspace_btn()
        self.appbar = self.view_appbar()
        self.page.appbar = self.appbar
        self.page.snack_bar = SnackBar(
            content=Text("")
        )
        self.page.snack_bar.open = False

        self.file_picker = FilePicker(on_result=self.on_select_workspace)
        self.page.overlay.append(self.file_picker)
        self.import_file_picker = FilePicker(on_result=self.on_import_file)
        self.page.overlay.append(self.import_file_picker)

        self.sidebar = Sidebar(self.page)
        self.sidebar.visible = private_key is not None

        self.password_input = self.view_password_input()
        self.file_viewer = FileViewer(self.page)
        
        event_bus.subscribe(Events.UPDATE_SIDEBAR, self.sidebar.update)
        event_bus.subscribe(Events.ADD_SECRET, self.on_add_secret)
        event_bus.subscribe(Events.FILE_SELECTED, self.on_file_selected)
        event_bus.subscribe(Events.ON_LOGGED_IN, self.update)

    
    def update(self):
        super().update()
        private_key = self.store.get_private_key()
        self.sidebar.visible = private_key is not None
        self.sidebar.update()
        if self.appbar is not None:
            self.page.appbar.actions = self.view_appbar_actions()
            self.page.appbar.update()
        self.page.update()  

    
    def build(self):
        return Container(
            expand=True,
            bgcolor=colors.RED_200,
            content=Row([
                self.sidebar,
                self.file_viewer
            ])
        )

    
    def did_mount(self):
        super().did_mount()
        self.sidebar.update()

    
    def will_unmount(self):
        event_bus.unsubscribe(Events.UPDATE_SIDEBAR, self.sidebar.update)
        event_bus.unsubscribe(Events.ADD_SECRET, self.on_add_secret)
        event_bus.unsubscribe(Events.FILE_SELECTED, self.on_file_selected)
        event_bus.unsubscribe(Events.ON_LOGGED_IN, self.update)
        return super().will_unmount()

    
    def on_add_secret(self):
        self.file_viewer.clear()
        self.file_viewer.visible = True
        self.file_viewer.on_create_secret()
        self.update()

    
    def on_file_selected(self, path: str):
        private_key = self.store.get_private_key()
        data = open(path, 'rb').read()
        decrypted_content = self.security.decrypt(private_key, data)
        if decrypted_content is None:
            self.page.snack_bar.content = Text("Error decrypting file")
            self.page.snack_bar.open = True
            self.update()
            return

        file_name = path.split("/")[-1]
        str_content = decrypted_content.decode('utf-8')
        workspace = self.store.get_workspace()
        file_viewer_content = FileViewerContent.from_file(workspace, file_name, str_content)

        self.file_viewer.on_file_selected(file_viewer_content)
        self.file_viewer.visible = True
        self.update()
    
    def on_enctryption_error(self, error: str):
        self.page.snack_bar.content = Text(error)
        self.page.snack_bar.open = True
        self.update()

    def view_workspace_title(self, workspace_tile: str) -> str:
        return Text(value=workspace_tile, size=16, weight="bold", color=colors.BLUE_GREY_900)

    def view_select_workspace_btn(self) -> ElevatedButton:
        btn_text = "Select Workspace"
        workspace = self.store.get_workspace()
        if workspace:
            btn_text = "Change Workspace"
        return ElevatedButton(text=btn_text, on_click=lambda _: self.file_picker.get_directory_path())

    def view_appbar_actions(self):
        return [
            Container(
                content=Row([
                    self.view_workspace_title(self.get_wokrspace_title_text()),
                    self.select_workspace_btn
                ]),
            ),
            Container(
                content=PopupMenuButton(
                    items=self.view_appbar_menu_items(),
                ),
                margin=margin.only(left=50, right=25)
            )
        ]
    def view_appbar_menu_items(self) -> list[PopupMenuItem]:
        items = []
        pkey = self.store.get_private_key()
        if pkey:
            email = self.store.get_email()
            btn_text = f"Logged in as {email}. Logout"
            items.append(PopupMenuItem(text=btn_text, on_click=self.on_logout))
            items.append(PopupMenuItem(text="Import from Lastpass", on_click=lambda _: self.import_file_picker.pick_files()))
        else:
            items.append(PopupMenuItem(text="Login", on_click=self.on_login))
        items.extend([
            PopupMenuItem(),  # divider
            PopupMenuItem(text="Settings")
        ])
        
        return items

    def view_appbar(self):
        return AppBar(
            leading=Icon(icons.SAFETY_CHECK),
            leading_width=10,
            title=Text("DistriLock", size=24, text_align="end"),
            center_title=False,
            toolbar_height=75,
            bgcolor=colors.LIGHT_BLUE_ACCENT_700,
            actions=self.view_appbar_actions()
        )

    def view_password_input(self):
        return TextField(label="Password", password=True, can_reveal_password=True)

    
    def on_login(self, event: ControlEvent):
        self.page.dialog = LoginDialog(self.page)
        self.page.dialog.open = True
        self.update()

    
    def on_logout(self, event: ControlEvent):
        self.store.delete_private_key()
        self.store.delete_public_key()
        self.store.delete_email()
        self.update()

    
    def get_wokrspace_title_text(self):
        workspace = self.store.get_workspace()
        if workspace is None:
            return "Now workspace selected"
        else:
            return f'Workspace: {workspace.split("/")[-1]}'

    
    def on_select_workspace(self, event: FilePickerResultEvent):
        workspace = event.path
        self.store.put_workspace(workspace)
        self.select_workspace_btn.text = "Change workspace"
        self.update()

    def on_import_file(self, event: FilePickerResultEvent):
        files = event.files
        if len(files) == 0:
            self.page.snack_bar.content = Text("No file selected")
            return

        if len(files) > 1:
            self.page.snack_bar.content = Text("Only one file can be selected")
            return

        file = files[0]
        path = file.path
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            workspace = self.store.get_workspace()
            public_key = self.store.get_public_key()
            for row in csv_reader:
                line_count += 1
                if line_count == 0:
                    continue
                else:
                    file_content = FileViewerContent(
                        url=row[0],
                        username=row[1],
                        password=row[2],
                        extra=row[4],
                        name=row[5],
                        tag=row[6],
                        fav=row[7],
                        file_type= FileType.WEB if row[0] else FileType.DEFAULT
                    )
                    file_name = file_content.get_file_name()
                    file_content = file_content.get_file_content()
                    encrypted_content = self.security.encrypt(public_key, file_content)
                    try:
                        file = open(f'{workspace}/{file_name}', "wb")
                        file.write(encrypted_content)
                        file.close()
                    except Exception as e:
                        print(e)
        print(f'Processed {line_count} lines.')
        self.update()


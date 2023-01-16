from flet import (
    UserControl,
    Container,
    TextField,
    IconButton,
    icons,
    Text,
    TextStyle,
    Dropdown,
    dropdown,
    Card,
    padding,
    Alignment,
    Column,
    Row,
    MainAxisAlignment,
    Divider,
    Page,
    colors
)
from button import (Button)
from delete_button import (DeleteButton)
from logger import (log)
from pyperclip import (copy)
from file_type import FileType, FILE_TYPE_VALUES
from os import remove
from flet.security import encrypt, decrypt
from constants import (SIDEBAR_WIDTH)
from events import event_bus, Events
from file_manager import FileManager
from store import Store

class FileViewer (UserControl):

    @log
    def __init__(self, page: Page):
        super().__init__()

        self.page = page

        self.file_viewer_copy_title_btn = self.view_copy_title_btn()
        self.file_viewer_copy_content_btn = self.view_copy_content_btn()
        self.file_viewer_title = self.view_file_viewer_title()
        self.file_viewer_content = self.view_file_viewer_content()
        self.file_viewer_save_btn = self.view_save_file_btn()
        self.file_viewer_edit_btn = self.view_edit_file_btn()
        self.file_viewer_delete_btn = self.view_delete_file_btn()
        self.file_viewer_file_type_picker = self.view_file_viewer_file_type_picker()
        self.visible = False
        self.store = Store(self.page)
        self.page.on_resize = self.on_page_resize

    def build(self):
        self.container = Container(
            width=self.get_file_viewer_width(),
            height=self.page.height,
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
                    Row(
                        [
                            self.file_viewer_file_type_picker
                        ]
                    ),
                    Divider(),
                    Row(
                        [
                            self.file_viewer_title, 
                            self.file_viewer_copy_title_btn
                        ]
                    ),
                    Divider(),
                    Row(
                        [
                            self.file_viewer_content,
                            self.file_viewer_copy_content_btn
                        ]
                    )
                ])
        )

        return Card(
            height=self.page.height,
            content=self.container
        )

    def update(self):
        super().update()
        event_bus.emit(Events.UPDATE_SIDEBAR)

    @log
    def clear(self):
        self.file_viewer_file_type_picker.value = FileType.DEFAULT
        self.file_viewer_title.value = ""
        self.file_viewer_content.value = ""
        self.update()

    @log
    def view_copy_title_btn(self) -> IconButton:
        return IconButton(
            icon=icons.COPY,
            on_click=lambda _: self.copy_to_clipboard(
                self.file_viewer_title.value)
        )

    @log
    def copy_to_clipboard(self, text):
        copy(text)
        self.page.snack_bar.content = Text("Copied to clipboard")
        self.page.snack_bar.open = True
        self.update()

    @log
    def view_copy_content_btn(self) -> IconButton:
        return IconButton(
            icon=icons.COPY,
            on_click=lambda _: self.copy_to_clipboard(
                self.file_viewer_content.value)
        )

    @log
    def view_file_viewer_title(self) -> TextField:
        return TextField(
            expand=True,
            label="Title",
            label_style=TextStyle(size=16, weight="bold"),
        )

    @log
    def view_file_viewer_content(self) -> TextField:
        return TextField(
            expand=True,
            multiline=True,
            label="Content",
            label_style=TextStyle(size=16, weight="bold"),
        )

    @log
    def view_save_file_btn(self) -> Button:
        btn = Button(text="Save", on_click=self.on_file_save_click)
        return btn

    @log
    def view_edit_file_btn(self) -> Button:
        btn = Button(text="Edit", on_click=self.on_file_edit_click)
        return btn

    @log
    def view_delete_file_btn(self) -> DeleteButton:
        btn = DeleteButton(text="Delete", on_click=self.on_file_delete_click)
        return btn

    @log
    def on_file_save_click(self, event):
        title = self.file_viewer_title.value
        content = self.file_viewer_content.value
        type = self.file_viewer_file_type_picker.value
        password = self.store.get_password()
        workspace = self.store.get_workspace()

        if password is None:
            self.page.snack_bar.content = Text(
                "You do not have a password set, please login first!")
            self.page.snack_bar.open = True
            self.update()
            return

        if title == "" or content == "":
            return

        self.file_viewer_edit_btn.set_disabled(False)
        self.file_viewer_save_btn.set_disabled(True)
        self.file_viewer_title.disabled = True
        self.file_viewer_content.disabled = True

        file_name = f'{type}#{title.replace(" ", "_")}'
        file = open(f'{workspace}/{file_name}.enc', "w")

        encrypted_content = encrypt(f'{title}\n{content}', password)
        file.write(encrypted_content)
        file.close()
        self.update()

    @log
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

    @log
    def on_file_delete_click(self, event):
        title = self.file_viewer_title.value
        type = self.file_viewer_file_type_picker.value
        workspace = self.store.get_workspace()
        file_name = f'{type}#{title.replace(" ", "_")}'
        file_path = f'{workspace}/{file_name}.enc'
        remove(file_path)
        self.update()

    @log
    def on_file_edit_click(self, event):
        self.file_viewer_edit_btn.set_disabled(True)
        self.file_viewer_save_btn.set_disabled(False)
        self.file_viewer_title.disabled = False
        self.file_viewer_content.disabled = False
        self.update()

    @log
    def get_file_viewer_width(self):
        return self.page.width - SIDEBAR_WIDTH - 20

    @log
    def on_page_resize(self, event):
        self.container.width = self.get_file_viewer_width()
        self.container.height = self.page.height
        self.update()

    @log
    def on_file_selected(self, file_path: str):
        password = self.store.get_password()
        workspace = self.store.get_workspace()
        file_content = FileManager(file_path, password, workspace).read()
        self.file_viewer_title.value = file_content.title
        self.file_viewer_content.value = file_content.content
        self.file_viewer_edit_btn.set_disabled(False)
        self.file_viewer_save_btn.set_disabled(True)
        self.file_viewer_delete_btn.set_disabled(False)
        self.file_viewer_title.disabled = True
        self.file_viewer_content.disabled = True
        self.file_viewer_file_type_picker.value = file_content.file_type
        self.update()

    @log
    def on_create_secret(self):
        self.file_viewer_title.value = ""
        self.file_viewer_content.value = ""
        self.file_viewer_edit_btn.set_disabled(True)
        self.file_viewer_delete_btn.set_disabled(True)
        self.file_viewer_save_btn.set_disabled(False)
        self.file_viewer_title.disabled = False
        self.file_viewer_content.disabled = False
        self.update()

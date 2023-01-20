from flet import (
    AlertDialog,
    Text,
    Container,
    Column,
    Row,
    Divider,
    TextField,
    TextButton,
    MainAxisAlignment,
    KeyboardType,
    UserControl
)

from events import event_bus, Events
from store import get_store
from security_manager import SecurityManager
from logger import log
from info_panel import InfoPanel, InfoPanelType

class LoginDialog(UserControl):

    
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.store = get_store(self.page)
        self.dialog: AlertDialog = None

        self.info_panel_email = InfoPanel(
            InfoPanelType.WARNING, 
            """Your email address is used to deterministically compute a hash used to share 
your public key with other users."""
        )
        
        self.info_panel_password = InfoPanel(
            InfoPanelType.WARNING,
            """Your password, in combination with your email address, is used to deterministically 
compute a set of private/public key pair that is used to encrypt/decrypt your secrets. 
Make sure you remember your password, as you will not be able to recover 
your secrets if you forget it!
            """
        )

        self.email_input = TextField(
            label="Email address", 
            keyboard_type=KeyboardType.EMAIL
        )

        self.password_input = TextField(
            label="Password", 
            password=True, 
            can_reveal_password=True
        )
        # self.dialog = self.get_view()
    
    
    def build(self):
        return self.get_view()
    
    
    def get_view(self):
        self.dialog = AlertDialog(
            modal=True,
            title=Text("Login"),
            open=True,
            content=Container(
                content=Column([
                    Row([
                        Text(
                            "Do not forget your credentials. Without them your secrets will be lost!")
                    ]),
                    Row([Divider()]),
                    Row([self.info_panel_email]),
                    Row([self.info_panel_password]),
                    Divider(),
                    Row([self.email_input]),
                    Row([self.password_input]),
                ])
            ),
            actions=[
                TextButton("Login", on_click=self.on_click),
                TextButton("Cancel", on_click=lambda e: self.set_open(False))
            ],
            actions_alignment=MainAxisAlignment.END,
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )
        return self.dialog

    
    def set_open(self, open: bool):
        self.dialog.open = open
        self.update()

    
    def on_click(self, event):
        password = self.password_input.value
        email = self.email_input.value
        security_manager = SecurityManager()
        (private_key, public_key) = security_manager.create_key_pair(email, password)
        self.store.put_private_key(private_key)
        self.store.put_public_key(public_key)
        self.store.put_email(email)
        event_bus.emit(Events.ON_LOGGED_IN)
        self.set_open(False)
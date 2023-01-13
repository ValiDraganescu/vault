from flet import (
    Page,
    colors,
    app
)

from vault_app import VaultApp


def main(page: Page):

    page.title = "Git Vault"
    page.padding = 0
    page.bgcolor = colors.BLUE_GREY_200
    app = VaultApp(page)
    page.add(app)
    page.update()

app(target=main)
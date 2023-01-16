from flet import Page


class Store:

    def __init__(self, page: Page):
        self.page = page

    def __put(self, key, value):
        self.page.client_storage.set(key, value)

    def __get(self, key):
        return self.page.client_storage.get(key)

    def put_workspace(self, workspace):
        self.__put("workspace", workspace)

    def get_workspace(self):
        return self.__get("workspace")

    def put_password(self, password):
        self.__put("password", password)

    def get_password(self):
        return self.__get("password")

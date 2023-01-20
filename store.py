from flet import Page
from nacl.public import PrivateKey, PublicKey

class Store:
    __instance = None
    in_memory_storage = {}

    @staticmethod
    def get_instance(page: Page):
        if Store.__instance == None:
            Store(page)
        return Store.__instance

    def __init__(self, page: Page):
        if Store.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.page = page
            Store.__instance = self

    def __put(self, key, value):
        self.page.client_storage.set(key, value)

    def __get(self, key):
        return self.page.client_storage.get(key)

    def put_workspace(self, workspace):
        self.__put("distrilock.workspace", workspace)

    def get_workspace(self):
        return self.__get("distrilock.workspace")

    def put_email(self, email):
        self.__put("distrilock.email", email)

    def get_email(self):
        return self.__get("distrilock.email")

    def delete_email(self):
        self.page.client_storage.remove("distrilock.email")

    def put_private_key(self, private_key: PrivateKey):
        self.in_memory_storage["distrilock.private_key"] = private_key

    def delete_private_key(self):
        del self.in_memory_storage["distrilock.private_key"]

    def get_private_key(self) -> PrivateKey:
        try:
            return self.in_memory_storage["distrilock.private_key"]
        except KeyError:
            return None

    def put_public_key(self, public_key: PublicKey):
        self.in_memory_storage["distrilock.public_key"] = public_key

    def delete_public_key(self):
        del self.in_memory_storage["distrilock.public_key"]

    def get_public_key(self) -> PublicKey:
        try:
            return self.in_memory_storage["distrilock.public_key"]
        except KeyError:
            return None

def get_store(page: Page):
    return Store.get_instance(page)
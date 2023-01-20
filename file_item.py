class FileItem:
    path: str
    name: str
    type: str

    def __init__(self, path: str):
        self.path = path
        self.name = path.split("/")[-1].split("#")[1].split(".enc")[0]
        self.type = self.get_file_type()

    # file name exaples:
    # web#google.com.enc
    # web#google.net.com.enc
    # app#facebook.enc
    # app#teamviwer.enc
    # this function returns the file type that is the part before the # sign
    def get_file_type(self) -> str:
        parts = self.path.split("/")[-1].split("#")[0]
        return parts
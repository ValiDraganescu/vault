
from flet.security import encrypt, decrypt
from file_viwer_content import FileViewerContent

class FileManager:

    def __init__(self, path: str, password: str, workspace: str):
        self.path = path
        self.password = password
        self.workspace = workspace

    def read(self) -> FileViewerContent:
        file_content = open(self.path, 'r').read()
        decrypted_content = decrypt(file_content, self.password)
        file_name = self.path.split("/")[-1]
        file_type = file_name.split("#")[0]
        rows = decrypted_content.split('\n')
        title = rows[0]
        content = '\n'.join(rows[1:])

        return FileViewerContent(title, content, file_type)

    def write(self, file_viewer_content: FileViewerContent):
        file_name = f'{type}#{file_viewer_content.title.replace(" ", "_")}'
        file = open(f'{self.workspace}/{file_name}.enc', "w")

        encrypted_content = encrypt(f'{file_viewer_content.title}\n{file_viewer_content.content}', self.password)
        file.write(encrypted_content)
        file.close()

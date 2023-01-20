from dataclasses import dataclass
from file_type import FileType
import unicodedata
import re

@dataclass
class FileViewerContent:
    name = ""
    url = ""
    username = ""
    password = ""
    extra = ""
    tag = ""
    fav = 0
    type = FileType.DEFAULT,
    file_path = ""
    file_name = ""

    def get_file_content(self):
        return f'''
        url:{self.url}
        username:{self.username}
        password:{self.password}
        extra:{self.extra}
        '''
    
    # file name format fav#tag#file_type#file_name
    @staticmethod
    def from_file(workspace: str, file_name: str, file_content: str):
        file_viewer_content = FileViewerContent.from_file_name(workspace, file_name)
        rows = file_content.split('\n')
        for row in rows:
            if "url" in row:
                file_viewer_content.url = row.split(":")[1]
            if "username" in row:
                file_viewer_content.username = row.split(":")[1]
            if "password" in row:
                file_viewer_content.password = row.split(":")[1]
            if "extra" in row:
                file_viewer_content.extra = row.split(":")[1]

        return file_viewer_content

    @staticmethod
    def from_file_name(workspace: str, file_name: str):
        file_name = file_name.replace('.enc', '')
        file_name = file_name.split('#')
        file_viewer_content = FileViewerContent()
        file_viewer_content.fav = int(file_name[0])
        file_viewer_content.tag = file_name[1]
        file_viewer_content.type = FileType(file_name[2])
        file_viewer_content.name = file_name[3]
        file_name = f'{file_viewer_content.fav}#{file_viewer_content.tag}#{file_viewer_content.type.value}#{file_viewer_content.name}.enc'
        file_name = slugify(file_name, allow_unicode=True)
        file_viewer_content.file_name = file_name
        file_viewer_content.file_path = f'{workspace}/{file_viewer_content.file_name}'
        return file_viewer_content

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens or #. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s#.-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
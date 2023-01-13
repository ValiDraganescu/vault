from enum import Enum

class FileType(Enum):
    WEB = "web"
    APP = "app"
    DEFAULT = "file"

FILE_TYPE_VALUES = {
    FileType.APP: 'Application',
    FileType.WEB: 'Website',
    FileType.DEFAULT: 'File'
}
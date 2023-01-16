from dataclasses import dataclass
from file_type import FileType

@dataclass
class FileViewerContent:
    title: str
    content: str
    file_type: FileType
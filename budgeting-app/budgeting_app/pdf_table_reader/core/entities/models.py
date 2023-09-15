from dataclasses import dataclass, asdict, field
from typing import Literal

from pdfplumber import table, page

BASE_IMAGE_RESOLUTION = 72


@dataclass
class ImageWrapper:
    image_bytes: list[bytes]
    page_indices: list[int] | Literal['all'] = field(default_factory=Literal['all'])
    resolution: int = field(default=BASE_IMAGE_RESOLUTION)
    _format: str = field(default='PNG')
    antialias: bool = field(default=False)
    
    
@dataclass
class PDFPageWrapper:
    page: page.Page
    base_size: tuple[int, int] = field(init=False)
    table_settings: table.T_table_settings = field(default_factory=lambda: {})
    
    def __post_init__(self) -> None:
        self.base_size = self.page.to_image(BASE_IMAGE_RESOLUTION).original.size
    
    
@dataclass
class PDFFileWrapper:
    pages: list[PDFPageWrapper]
    image: ImageWrapper | None = field(default=None)

    def to_dict(self) -> dict:
        return {
            'pages': [asdict(p) for p in self.pages],
            'image': None if self.image is None else asdict(self.image)
        }

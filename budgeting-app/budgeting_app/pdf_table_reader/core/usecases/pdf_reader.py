import pdfplumber

from budgeting_app.utils.types import T_pdf_file_path
from budgeting_app.utils.validators import is_pdf_file_path
from budgeting_app.pdf_table_reader.core.entities.models import (
    PDFFileWrapper,
    PDFPageWrapper,
    BASE_IMAGE_RESOLUTION
)


class PDFReader:
    @classmethod
    def open(cls, file_path: T_pdf_file_path, password: str | None = None) -> PDFFileWrapper:

        if is_pdf_file_path(file_path):
            pdf = pdfplumber.open(path_or_fp=file_path, password=password)

            pdf_file = PDFFileWrapper(pages=[])

            for page in pdf.pages:
                pdf_file.pages.append(PDFPageWrapper(page))

            return pdf_file

        else:
            raise TypeError('Given path is not a valid string pointing to a pdf file.')

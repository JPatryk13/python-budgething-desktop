import pdfplumber

from budgeting_app.utils.types import T_pdf_file_path
from budgeting_app.utils.validators import is_pdf_file_path
from budgeting_app.utils.logging import CustomLoggerAdapter
from budgeting_app.pdf_table_reader.core.entities.models import (
    PDFFileWrapper,
    PDFPageWrapper
)


class PDFReader:
    
    @classmethod
    def open(cls, filepath: T_pdf_file_path, password: str | None = None) -> PDFFileWrapper | None:
        
        logger = CustomLoggerAdapter.getLogger('pdf_table_reader', className='PDFReader')

        if is_pdf_file_path(filepath):
            logger.debug('Path to the PDF file is valid.')
            
            pdf = pdfplumber.open(path_or_fp=filepath, password=password)

            pdf_file = PDFFileWrapper(pages=[])

            for page in pdf.pages:
                pdf_file.pages.append(PDFPageWrapper(page))
                
            logger.debug(f'Successfully created PDFFileWrapper with {len(pdf_file.pages)} pages.')

            return pdf_file

        else:
            logger.error('Given path is not a valid string pointing to a pdf file.')

from typing import TypeAlias

from pdfplumber._typing import T_point

T_uuid4_string: TypeAlias = str
T_posix_timestamp: TypeAlias = int
T_pdf_file_path: TypeAlias = str
T_line: TypeAlias = tuple[T_point, T_point]
T_nonnegative_float: TypeAlias = float
T_iso4217_currency_code: TypeAlias = str
T_raw_data: TypeAlias = list[str | list[str | None] | None]
T_normalised_raw_data: TypeAlias = list[str]

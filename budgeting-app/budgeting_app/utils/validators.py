from datetime import datetime
from typing import Any
from uuid import UUID

from budgeting_app.utils.types import T_line

def is_uuid4_string(u: Any) -> bool:
    if isinstance(u, str):
        try:
            uuid_obj = UUID(hex=u, version=4)
            # Ensure the UUID string representation is the same as the original input
            return str(uuid_obj) == u
        except Exception:
            return False
    else:
        return False


def is_posix_timestamp(t: Any) -> bool:
    if isinstance(t, int):
        try:
            datetime.fromtimestamp(t)
            return True
        except Exception:
            return False
    else:
        return False


def is_pdf_file_path(p: Any) -> bool:
    if isinstance(p, str):
        return p.endswith('.pdf')

    return False


def is_num(n: Any) -> bool:
    return isinstance(n, (int, float))


def is_point(p: Any) -> bool:
    if isinstance(p, tuple):
        if len(p) == 2:
            return is_num(p[0]) and is_num(p[1])

    return False


def is_line(l: Any) -> bool:
    if isinstance(l, tuple):
        if len(l) == 2:
            return is_point(l[0]) and is_point(l[1])

    return False

def is_vertical_line(l: T_line, tolerance: float = 0.5) -> bool:
    (x0, _), (x1, _) = l
    return x1 - abs(tolerance) <= x0 <= x1 + abs(tolerance)

def is_horizontal_line(l: T_line, tolerance: float = 0.5) -> bool:
    (_, y0), (_, y1) = l
    return y1 - abs(tolerance) <= y0 <= y1 + abs(tolerance)

def is_bbox(b: Any) -> bool:
    if isinstance(b, tuple):
        if len(b) == 4:
            return all(list(map(lambda num: is_num(num), b)))


def is_nonnegative_float(f: Any) -> bool:
    if isinstance(f, float):
        return f >= 0.0
    else:
        return False


def is_iso4217_currency_code(c: Any) -> bool:
    if isinstance(c, str):
        if len(c) == 3:
            return c.isupper()

    return False


def is_normalised_raw_data(t: Any) -> bool:
    if isinstance(t, list):
        return all(list(map(lambda c: isinstance(c, str), t)))

    return False

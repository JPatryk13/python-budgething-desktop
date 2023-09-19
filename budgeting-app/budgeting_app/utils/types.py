import threading
from typing import Any, Callable, TypeAlias, Generic, TypeVar

from pdfplumber._typing import T_point

T_uuid4_string: TypeAlias = str
T_posix_timestamp: TypeAlias = int
T_pdf_file_path: TypeAlias = str
T_line: TypeAlias = tuple[T_point, T_point]
T_nonnegative_float: TypeAlias = float
T_iso4217_currency_code: TypeAlias = str
T_raw_data: TypeAlias = list[str | list[str | None] | None]
T_normalised_raw_data: TypeAlias = list[str]
            
class TypedObservableDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._callbacks: list[Callable[[str, Any], None]] = []
        self._lock = threading.Lock()

    def __setitem__(self, key: str, value: Any):
        print(f'ObservableDict.__setitem__: key={key}, value={value}')
        with self._lock:
            super().__setitem__(key, value)
            self._notify_observers(key, value)

    def add_callback(self, callback: Callable[[str, Any], None]):
        print('ObservableDict.add_callback')
        with self._lock:
            self._callbacks.append(callback)

    def _notify_observers(self, key: str, value: Any):
        print(f'ObservableDict._notify_observers: key={key}, value={value}')
        for callback in self._callbacks:
            callback(key, value)
            

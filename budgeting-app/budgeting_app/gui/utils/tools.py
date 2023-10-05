import math
from typing import Any, Callable, Literal, TypedDict
from unittest import TestCase
from dataclasses import asdict

from PyQt6 import QtWidgets, QtCore
from budgeting_app.utils.tools import is_all_not_none

DEFAULT_SPINBOX_WIDTH = 40

def create_spinbox(
    _min: int,
    _set: int,
    *,
    _max: int | None = None,
    _label: str | None = None,
    _width: int = DEFAULT_SPINBOX_WIDTH
) -> tuple[QtWidgets.QWidget, QtWidgets.QSpinBox]:
    
    container_widget = QtWidgets.QWidget()
    container_widget_layout = QtWidgets.QHBoxLayout()

    if _label not in [None, ""]:
        label = QtWidgets.QLabel(_label)
        container_widget_layout.addWidget(label)

    spinbox = QtWidgets.QSpinBox()
    spinbox.setValue(int(_set))
    spinbox.setMinimum(int(_min))
    if _max is not None:
        spinbox.setMaximum(int(_max))
    spinbox.setFixedWidth(int(_width))
    container_widget_layout.addWidget(spinbox)

    container_widget.setLayout(container_widget_layout)

    return container_widget, spinbox

def create_spinbox_with_label(
    _label: str,
    _min: int,
    _set: int,
    _max: int | None = None,
    _width: int = DEFAULT_SPINBOX_WIDTH
) -> tuple[QtWidgets.QWidget, QtWidgets.QSpinBox]:
    
    return create_spinbox(
        _min,
        _set,
        _max=_max,
        _label=_label,
        _width=_width
    )
    
def create_dropdown_with_label(
    _label: str,
    _items: list[str],
    _default_index: int
) -> tuple[QtWidgets.QWidget, QtWidgets.QComboBox]:
    container_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel(_label)
    layout.addWidget(label)
    dropdown = QtWidgets.QComboBox()
    dropdown.addItems(_items)
    dropdown.setCurrentIndex(_default_index)
    layout.addWidget(dropdown)
    container_widget.setLayout(layout)

    return container_widget, dropdown

def create_text_area_with_label(
    _label: str,
    _label_postion: Literal['top', 'left', 'inside'],
    *,
    _echo_mode: QtWidgets.QLineEdit.EchoMode | None = None
) -> tuple[QtWidgets.QWidget, QtWidgets.QLineEdit]:
    
    container_widget = QtWidgets.QWidget()
    
    if _label_postion == 'top':
        layout = QtWidgets.QVBoxLayout()
    else:
        layout = QtWidgets.QHBoxLayout()
        
    if _label_postion != 'inside':
        label = QtWidgets.QLabel(_label)
        layout.addWidget(label)
    
    text_area = QtWidgets.QLineEdit()
    
    if _label_postion == 'inside':
        text_area.setPlaceholderText(_label)
        
    if _echo_mode is not None:
        text_area.setEchoMode(_echo_mode)
        
    layout.addWidget(text_area)
    
    container_widget.setLayout(layout)
    
    return container_widget, text_area

def create_checkbox_with_label(
    _label: str | None = None,
    _label_postion: Literal['top', 'left', 'right'] = 'left',
    _set_checked: QtCore.Qt.CheckState = QtCore.Qt.CheckState.Unchecked
) -> tuple[QtWidgets.QWidget, QtWidgets.QCheckBox]:
    
    if _label_postion in ['left', 'right']:
        layout = QtWidgets.QHBoxLayout()
    else:
        layout = QtWidgets.QVBoxLayout()
        
    container_widget = QtWidgets.QWidget()
    container_widget.setLayout(layout)
    
    if _label is not None:
        if _label_postion in ['left', 'top']:
            # add label before checkbox
            layout.addWidget(QtWidgets.QLabel(_label))
            
    cbox = QtWidgets.QCheckBox()
    cbox.setCheckState(_set_checked)
    layout.addWidget(cbox)
    
    if _label is not None:
        if _label_postion == 'right':
            # add label after checkbox
            layout.addWidget(QtWidgets.QLabel(_label))
            
    return container_widget, cbox
    
    
class ExpandableSpinBoxList:
    
    class QSpinBoxWrapper(TypedDict):
        value_uuid: str
        container_widget: QtWidgets.QWidget
        sbox: QtWidgets.QSpinBox
        
    main_container: QtWidgets.QWidget
    sbox_list: list[QSpinBoxWrapper]
    
    button_text: str
    _min: int | None
    _set: int
    _max: int | None
    width: int
    
    button: QtWidgets.QPushButton
    add_value: Callable[[int], str]
    update_value: Callable[[str, int], None]
    remove_value: Callable[[str], None]
    
    def __init__(
        self,
        *,
        button_text: str,
        _min: int | None = None,
        _set: int | None = None,
        _max: int | None = None,
        width: int = DEFAULT_SPINBOX_WIDTH
    ) -> None:
        self.sbox_list = []
        self.button_text = button_text
        self._min = _min
        self._max = _max
        self.width = width
        
        if _set is not None:
            self._set = _set
        else:
            if _min is not None:
                self._set = _min
            elif _max is not None:
                self._set = _max
            else:
                self._set = 0
        
        self._create_main_container()
        self.button.clicked.connect(self.__add_sbox)
     
    def values_from_list(self, values: list[dict[Literal['uuid', 'value'], str | int]]) -> None:
        # set all container widgets to delete later
        for exisiting_wrapper in self.sbox_list:
            exisiting_wrapper['container_widget'].deleteLater()
            
        # empty the list
        self.sbox_list = []
        
        # add new ones from the list
        for val in values:
            self.__add_sbox(**val)
        
    def __sbox_val_changed(self, sbox_wrapper: QSpinBoxWrapper) -> None:
        self.update_value(sbox_wrapper['value_uuid'], sbox_wrapper['sbox'].value())
        
    def _create_main_container(self) -> None:
        self.main_container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton()
        self.button.setText(self.button_text)
        layout.addWidget(self.button)
        self.main_container.setLayout(layout)
        
    def __add_sbox(
        self,
        *,
        uuid: int | None = None,
        value: str | None = None
    ) -> None:
        # check if the callables were given
        if not is_all_not_none(
            getattr(self, 'add_value', None),
            getattr(self, 'update_value', None),
            getattr(self, 'remove_value', None)
        ):
            raise ValueError(f'One or more functions is missing.\n\tadd_value={getattr(self, "add_value", None)}\n\tupdate_value={getattr(self, "update_value", None)}\n\tremove_value={getattr(self, "remove_value", None)}')
        
        # create spin box
        sbox_container, sbox = create_spinbox(
            self._min,
            self._set if value is None else value,
            _max=self._max,
            _width=self.width
        )
        sbox_wrapper: self.QSpinBoxWrapper = {
            'sbox': sbox,
            'container_widget': sbox_container,
            'value_uuid': self.add_value(self._set) if uuid is None else uuid
        }
        sbox.valueChanged.connect(lambda: self.__sbox_val_changed(sbox_wrapper))
        # create close button
        close_button = QtWidgets.QPushButton()
        close_button.setText('X')
        close_button.clicked.connect(lambda: self.__remove_sbox(sbox_wrapper))
        sbox_container.layout().addWidget(close_button)
        # add sbox and it's container to corresponding lists and the main widget container
        self.sbox_list.append(sbox_wrapper)
        self.main_container.layout().addWidget(sbox_container)
        
    def __remove_sbox(self, sbox_wrapper: QSpinBoxWrapper) -> None:
        self.sbox_list.remove(sbox_wrapper)
        self.remove_value(sbox_wrapper['value_uuid'])
        sbox_wrapper['container_widget'].deleteLater()

class PyQtAssert:
    @staticmethod
    def equalLines(QLine1: QtCore.QLineF | QtCore.QLine, QLine2: QtCore.QLineF | QtCore.QLine) -> None:
        arr1 = [QLine1.p1(), QLine1.p2()]
        arr2 = [QLine2.p1(), QLine2.p2()]
        equal = PyQtAssert.equalPointsArray(arr1, arr2)
        if not equal:
            TestCase().fail(f'QLine1 and QLine2 are not the same.\n\tQLine1={QLine1}\n\tQLine2={QLine2}')

    @staticmethod
    def equalRectangles(QRect1: QtCore.QRectF | QtCore.QRect, QRect2: QtCore.QRectF | QtCore.QRect) -> None:
        arr1 = [QRect1.topLeft(), QRect1.topRight(), QRect1.bottomLeft(), QRect1.bottomRight()]
        arr2 = [QRect2.topLeft(), QRect2.topRight(), QRect2.bottomLeft(), QRect2.bottomRight()]
        equal = PyQtAssert.equalPointsArray(arr1, arr2)
        if not equal:
            TestCase().fail(f'QRect1 and QRect2 are not the same.\n\tQRect1={QRect1}\n\tQRect2={QRect2}')

    @staticmethod
    def equalTables(table1: dict, table2: dict) -> None:
        if not isinstance(table1, dict) and not isinstance(table2, dict):
            raise TypeError(f'Both table1 and table2 must by dict-type. Got table1: {type(table1)} and table2: {type(table2)} instead.')
        
        TestCase().assertEqual(set(table1.keys()), set(['boundary', 'vertical_separators', 'horizontal_separators']), f'table1={table1}\ntable2={table2}')
        TestCase().assertEqual(set(table2.keys()), set(['boundary', 'vertical_separators', 'horizontal_separators']), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table1['boundary'], QtCore.QRectF), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table2['boundary'], QtCore.QRectF), f'table1={table1}\ntable2={table2}')

        TestCase().assertTrue(isinstance(table1['vertical_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda vline: isinstance(vline, QtCore.QLineF), table1['vertical_separators'])), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table2['vertical_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda vline: isinstance(vline, QtCore.QLineF), table2['vertical_separators'])), f'table1={table1}\ntable2={table2}')

        TestCase().assertTrue(isinstance(table1['horizontal_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda hline: isinstance(hline, QtCore.QLineF), table1['horizontal_separators'])), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table2['horizontal_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda hline: isinstance(hline, QtCore.QLineF), table2['horizontal_separators'])), f'table1={table1}\ntable2={table2}')

        PyQtAssert.equalRectangles(table1['boundary'], table2['boundary'])
        
        TestCase().assertEqual(len(table1['vertical_separators']), len(table2['vertical_separators']), f'table1={table1}\ntable2={table2}')
        for i, vline in enumerate(table2['vertical_separators']):
            PyQtAssert.equalLines(table1['vertical_separators'][i], vline)

        TestCase().assertEqual(len(table1['horizontal_separators']), len(table2['horizontal_separators']), f'table1={table1}\ntable2={table2}')
        for i, hline in enumerate(table2['horizontal_separators']):
            PyQtAssert.equalLines(table1['horizontal_separators'][i], hline)
        
    @staticmethod
    def equalPointsArray(_arr1: list[QtCore.QPoint | QtCore.QPointF], _arr2: list[QtCore.QPoint | QtCore.QPointF], _fail_if_false: bool = False) -> bool | None:
        """ Use only when elements are neither hashable nor sortable! """
        
        # convert QtCore.QPointF to tuples of floats and round each to get rid of the inequalities
        # far behind the decimal place
        arr1 = list(map(lambda p: (round(p.x(), 3), round(p.y(), 3)), _arr1))
        arr2 = list(map(lambda p: (round(p.x(), 3), round(p.y(), 3)), _arr2))
            
        unmatched = list(arr2)
        for element in arr1:
            try:
                unmatched.remove(element)
            except ValueError:
                if _fail_if_false:
                    TestCase().fail(f'arr1 and arr2 are not the same.\n\tarr1={arr1}\n\tarr2={arr2}')
                else:
                    return False
        if not _fail_if_false:
            return True
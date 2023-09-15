import math
from typing import Literal
from unittest import TestCase
from dataclasses import asdict


from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit
)
from PyQt6.QtCore import (
    QLine,
    QLineF,
    QRect,
    QRectF,
    QPoint,
    QPointF
)

DEFAULT_SPINBOX_WIDTH = 40

def create_spinbox(
    _min: int,
    _set: int,
    *,
    _max: int | None = None,
    _label: str | None = None,
    _width: int = DEFAULT_SPINBOX_WIDTH
) -> tuple[QWidget, QSpinBox]:
    
    container_widget = QWidget()
    container_widget_layout = QHBoxLayout()

    if _label not in [None, ""]:
        label = QLabel(_label)
        container_widget_layout.addWidget(label)

    spinbox = QSpinBox()
    spinbox.setValue(_set)
    spinbox.setMinimum(_min)
    if _max is not None:
        spinbox.setMaximum(_max)
    spinbox.setFixedWidth(_width)
    container_widget_layout.addWidget(spinbox)

    container_widget.setLayout(container_widget_layout)

    return container_widget, spinbox

def create_spinbox_with_label(
    _label: str,
    _min: int,
    _set: int,
    _max: int | None = None,
    _width: int = DEFAULT_SPINBOX_WIDTH
) -> tuple[QWidget, QSpinBox]:
    
    return create_spinbox(
        _min,
        _set,
        _max=_max,
        _label=_label,
        _width=_width
    )
    
def add_removable_widget(
    _subject_widget: QWidget,
    _container_widget: QWidget,
    _register: list[QWidget]
) -> None:
    """Add widget `_subject_widget` to `_container_widget` and `_register`.

    Args:
        _subject_widget (QWidget): Widget to be added
        _container_widget (QWidget): Widget to add the _subject_widget to
        _register (list[QWidget]): List storing all added widgets
    """
    def remove_widget(_w: QWidget, _l: list[QWidget]) -> None:
        _l.remove(_w)
        _w.deleteLater()
        
    close_button = QPushButton()
    close_button.setText('X')
    close_button.clicked.connect(lambda: remove_widget(_subject_widget, _register))
    _subject_widget.layout().addWidget(close_button)
    _register.append(_subject_widget)
    _container_widget.layout().addWidget(_subject_widget)
    
    

def add_removable_spinbox_to_widget(
    w: QWidget,
    l: list[QWidget],
    _min: int,
    _set: int,
    _max: int | None = None,
    _width: int = DEFAULT_SPINBOX_WIDTH
) -> None:
    """
    Add spin box to the widget `w` and list `l`.
    """
    def remove_spin_box(_w: QWidget, _l: list[QWidget]) -> None:
        _l.remove(_w)
        _w.deleteLater()

    spin_box_container, _ = create_spinbox(
        _min,
        _set,
        _max=_max,
        _width=_width
    )
    close_button = QPushButton()
    close_button.setText('X')
    close_button.clicked.connect(lambda: remove_spin_box(spin_box_container, l))
    spin_box_container.layout().addWidget(close_button)
    l.append(spin_box_container)
    w.layout().addWidget(spin_box_container)


def create_button_with_closeable_spinboxes(
    _button_text: str,
    _spin_box_list: list[QWidget],
    _min: int,
    _set: int,
    _max: int | None = None,
    _width: int = DEFAULT_SPINBOX_WIDTH
) -> QWidget:
    container_widget = QWidget()
    layout = QVBoxLayout()
    button = QPushButton()
    button.setText(_button_text)
    button.clicked.connect(lambda: add_removable_spinbox_to_widget(
        container_widget,
        _spin_box_list,
        _min,
        _set,
        _max,
        _width
    ))
    layout.addWidget(button)
    container_widget.setLayout(layout)

    return container_widget


def create_dropdown_with_label(
    _label: str,
    _items: list[str],
    _default_index: int
) -> tuple[QWidget, QComboBox]:
    container_widget = QWidget()
    layout = QVBoxLayout()
    label = QLabel(_label)
    layout.addWidget(label)
    dropdown = QComboBox()
    dropdown.addItems(_items)
    dropdown.setCurrentIndex(_default_index)
    layout.addWidget(dropdown)
    container_widget.setLayout(layout)

    return container_widget, dropdown

def create_text_area_with_label(
    _label: str,
    _label_postion: Literal['top', 'left', 'inside'],
    *,
    _echo_mode: QLineEdit.EchoMode | None = None
) -> tuple[QWidget, QLineEdit]:
    
    container_widget = QWidget()
    
    if _label_postion == 'top':
        layout = QVBoxLayout()
    else:
        layout = QHBoxLayout()
        
    if _label_postion != 'inside':
        label = QLabel(_label)
        layout.addWidget(label)
    
    text_area = QLineEdit()
    
    if _label_postion == 'inside':
        text_area.setPlaceholderText(_label)
        
    if _echo_mode is not None:
        text_area.setEchoMode(_echo_mode)
        
    layout.addWidget(text_area)
    
    container_widget.setLayout(layout)
    
    return container_widget, text_area

def create_button_with_closeable_widgets(
    _button_text: str,
    _closeable_widget: QWidget,
    _closeable_widget_list: list[QWidget]
) -> QWidget:
    container_widget = QWidget()
    layout = QVBoxLayout()
    button = QPushButton()
    button.setText(_button_text)
    
    button.clicked.connect(lambda: add_removable_widget(
        _closeable_widget,
        container_widget,
        _closeable_widget_list
    ))
    layout.addWidget(button)
    container_widget.setLayout(layout)

    return container_widget

class PyQtAssert:
    @staticmethod
    def equalLines(qline1: QLineF | QLine, qline2: QLineF | QLine) -> None:
        arr1 = [qline1.p1(), qline1.p2()]
        arr2 = [qline2.p1(), qline2.p2()]
        equal = PyQtAssert.equalPointsArray(arr1, arr2)
        if not equal:
            TestCase().fail(f'qline1 and qline2 are not the same.\n\tqline1={qline1}\n\tqline2={qline2}')

    @staticmethod
    def equalRectangles(qrect1: QRectF | QRect, qrect2: QRectF | QRect) -> None:
        arr1 = [qrect1.topLeft(), qrect1.topRight(), qrect1.bottomLeft(), qrect1.bottomRight()]
        arr2 = [qrect2.topLeft(), qrect2.topRight(), qrect2.bottomLeft(), qrect2.bottomRight()]
        equal = PyQtAssert.equalPointsArray(arr1, arr2)
        if not equal:
            TestCase().fail(f'qrect1 and qrect2 are not the same.\n\tqrect1={qrect1}\n\tqrect2={qrect2}')

    @staticmethod
    def equalTables(table1: dict, table2: dict) -> None:
        if not isinstance(table1, dict) and not isinstance(table2, dict):
            raise TypeError(f'Both table1 and table2 must by dict-type. Got table1: {type(table1)} and table2: {type(table2)} instead.')
        
        TestCase().assertEqual(set(table1.keys()), set(['boundary', 'vertical_separators', 'horizontal_separators']), f'table1={table1}\ntable2={table2}')
        TestCase().assertEqual(set(table2.keys()), set(['boundary', 'vertical_separators', 'horizontal_separators']), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table1['boundary'], QRectF), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table2['boundary'], QRectF), f'table1={table1}\ntable2={table2}')

        TestCase().assertTrue(isinstance(table1['vertical_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda vline: isinstance(vline, QLineF), table1['vertical_separators'])), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table2['vertical_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda vline: isinstance(vline, QLineF), table2['vertical_separators'])), f'table1={table1}\ntable2={table2}')

        TestCase().assertTrue(isinstance(table1['horizontal_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda hline: isinstance(hline, QLineF), table1['horizontal_separators'])), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(isinstance(table2['horizontal_separators'], list), f'table1={table1}\ntable2={table2}')
        TestCase().assertTrue(all(map(lambda hline: isinstance(hline, QLineF), table2['horizontal_separators'])), f'table1={table1}\ntable2={table2}')

        PyQtAssert.equalRectangles(table1['boundary'], table2['boundary'])
        
        TestCase().assertEqual(len(table1['vertical_separators']), len(table2['vertical_separators']), f'table1={table1}\ntable2={table2}')
        for i, vline in enumerate(table2['vertical_separators']):
            PyQtAssert.equalLines(table1['vertical_separators'][i], vline)

        TestCase().assertEqual(len(table1['horizontal_separators']), len(table2['horizontal_separators']), f'table1={table1}\ntable2={table2}')
        for i, hline in enumerate(table2['horizontal_separators']):
            PyQtAssert.equalLines(table1['horizontal_separators'][i], hline)
        
    @staticmethod
    def equalPointsArray(_arr1: list[QPoint | QPointF], _arr2: list[QPoint | QPointF], _fail_if_false: bool = False) -> bool | None:
        """ Use only when elements are neither hashable nor sortable! """
        
        # convert QPointF to tuples of floats and round each to get rid of the inequalities
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
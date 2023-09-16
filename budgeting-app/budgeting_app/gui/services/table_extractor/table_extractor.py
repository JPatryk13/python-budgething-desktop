import sys
from typing import Any

from PyQt6 import QtWidgets, QtCore

from budgeting_app.gui.utils.tools import (
    create_dropdown_with_label,
    create_spinbox_with_label,
    create_button_with_closeable_spinboxes
)
from budgeting_app.gui.services.table_extractor.image_tools import QTableF, Tools, PythonicTableData
from budgeting_app.gui.services.table_extractor.image_viewer import ImageViewer
from budgeting_app.gui.services.base import MainWindow
from budgeting_app.pdf_table_reader.core.entities.models import PDFFileWrapper
from budgeting_app.pdf_table_reader.core.usecases.table_detector_workspace import TableDetectorWorkspace
from budgeting_app.utils.tools import is_all_not_none

class TableSettingsWidgets:
    # table settings for pdfplumber
    vertical_strategy_widget: QtWidgets.QWidget
    horizontal_strategy_widget: QtWidgets.QWidget
    explicit_vertical_lines_widget: QtWidgets.QWidget
    explicit_vertical_lines_widget_list: list[QtWidgets.QWidget]
    explicit_horizontal_lines_widget: QtWidgets.QWidget
    explicit_horizontal_lines_widget_list: list[QtWidgets.QWidget]
    snap_tolerance_widget: QtWidgets.QWidget
    snap_x_tolerance_widget: QtWidgets.QWidget
    snap_y_tolerance_widget: QtWidgets.QWidget
    join_tolerance_widget: QtWidgets.QWidget
    join_x_tolerance_widget: QtWidgets.QWidget
    join_y_tolerance_widget: QtWidgets.QWidget
    edge_min_length_widget: QtWidgets.QWidget
    min_words_vertical_widget: QtWidgets.QWidget
    min_words_horizontal_widget: QtWidgets.QWidget
    keep_blank_chars_widget: QtWidgets.QWidget
    text_tolerance_widget: QtWidgets.QWidget
    text_x_tolerance_widget: QtWidgets.QWidget
    text_y_tolerance_widget: QtWidgets.QWidget
    intersection_tolerance_widget: QtWidgets.QWidget
    intersection_x_tolerance_widget: QtWidgets.QWidget
    intersection_y_tolerance_widget: QtWidgets.QWidget
    
    def __init__(self) -> None:
        self.vertical_strategy_widget, _ = create_dropdown_with_label(
            "Vertical strategy:",
            ["lines", "lines_strict", "text", "explicit"],
            1
        )

        self.horizontal_strategy_widget, _ = create_dropdown_with_label(
            "Horizontal strategy:",
            ["lines", "lines_strict", "text", "explicit"],
            1
        )

        self.explicit_vertical_lines_widget_list = []
        self.explicit_vertical_lines_widget = create_button_with_closeable_spinboxes(
            "Add vertical line",
            self.explicit_vertical_lines_widget_list,
            0,
            0
        )

        self.explicit_horizontal_lines_widget_list = []
        self.explicit_horizontal_lines_widget = create_button_with_closeable_spinboxes(
            "Add horizontal line",
            self.explicit_horizontal_lines_widget_list,
            0,
            0
        )

        self.snap_tolerance_widget, _ = create_spinbox_with_label("Snap tolerance: ", 0, 3)

        self.snap_x_tolerance_widget, _ = create_spinbox_with_label("Snap x tolerance: ", 0, 3)

        self.snap_y_tolerance_widget, _ = create_spinbox_with_label("Snap y tolerance: ", 0, 3)

        self.join_tolerance_widget, _ = create_spinbox_with_label("Join tolerance: ", 0, 3)

        self.join_x_tolerance_widget, _ = create_spinbox_with_label("Join x tolerance: ", 0, 3)

        self.join_y_tolerance_widget, _ = create_spinbox_with_label("Join y tolerance: ", 0, 3)

        self.edge_min_length_widget, _ = create_spinbox_with_label("Edge min length: ", 0, 3)

        self.min_words_vertical_widget, _ = create_spinbox_with_label("Min words vertical: ", 0, 3)

        self.min_words_horizontal_widget, _ = create_spinbox_with_label("Min words horizontal: ", 0, 1)

        self.keep_blank_chars_widget = QtWidgets.QWidget()
        keep_blank_chars_layout = QtWidgets.QHBoxLayout()
        keep_blank_chars_label = QtWidgets.QLabel("Keep blank chars: ")
        keep_blank_chars_layout.addWidget(keep_blank_chars_label)
        keep_blank_chars_value = QtWidgets.QRadioButton()
        keep_blank_chars_value.setChecked(False)
        keep_blank_chars_layout.addWidget(keep_blank_chars_value)
        self.keep_blank_chars_widget.setLayout(keep_blank_chars_layout)

        self.text_tolerance_widget, _ = create_spinbox_with_label("Text tolerance: ", 0, 3)

        self.text_x_tolerance_widget, _ = create_spinbox_with_label("Text x tolerance: ", 0, 3)

        self.text_y_tolerance_widget, _ = create_spinbox_with_label("Text y tolerance: ", 0, 3)

        self.intersection_tolerance_widget, _ = create_spinbox_with_label("Intersection tolerance: ", 0, 3)

        self.intersection_x_tolerance_widget, _ = create_spinbox_with_label("Intersection x tolerance: ", 0, 3)

        self.intersection_y_tolerance_widget, _ = create_spinbox_with_label("Intersection y tolerance: ", 0, 3)

    def get_all_widgets(self) -> list[QtWidgets.QWidget]:
        return [
            self.vertical_strategy_widget,
            self.horizontal_strategy_widget,
            self.explicit_vertical_lines_widget,
            self.explicit_horizontal_lines_widget,
            self.snap_tolerance_widget,
            self.snap_x_tolerance_widget,
            self.snap_y_tolerance_widget,
            self.join_tolerance_widget,
            self.join_x_tolerance_widget,
            self.join_y_tolerance_widget,
            self.edge_min_length_widget,
            self.min_words_vertical_widget,
            self.min_words_horizontal_widget,
            self.keep_blank_chars_widget,
            self.text_tolerance_widget,
            self.text_x_tolerance_widget,
            self.text_y_tolerance_widget,
            self.intersection_tolerance_widget,
            self.intersection_x_tolerance_widget,
            self.intersection_y_tolerance_widget
        ]

class TableExtractor(MainWindow):

    # editing_tools_widget hosts tool buttons and optionally table_size_widget
    editing_tools_widget: QtWidgets.QWidget
    editing_tools_layout: QtWidgets.QVBoxLayout

    # tool buttons residing in editing_tools_widget
    table_drawing_tool_button: QtWidgets.QPushButton
    hand_tool_button: QtWidgets.QPushButton
    
    # the spinboxes that allow to adjust the number of columns and rows
    table_size_widget: QtWidgets.QWidget
    table_size_widget_active: bool
    column_count_spinbox: QtWidgets.QSpinBox
    row_count_spinbox: QtWidgets.QSpinBox
    
    # table settings for pdfplumber
    table_settings_widgets: TableSettingsWidgets

    # the pane that shows on the left and contains table
    table_widget: QtWidgets.QTableWidget
    # list of created tables /w (col_count, row_count)
    tables: list[PythonicTableData]
    # the img viewer
    image_viewer: ImageViewer
    # table detector workspace
    table_detector_workspace: TableDetectorWorkspace
    

    def __init__(self, parent: Any | None = None):
        super().__init__(parent)
        self.setWindowTitle("Budgeting App - Table Extractor")
        # self.setGeometry(self.window_default_geometry)

        self.tables = []

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Create a splitter for the table and image viewer
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # Left widget (Table Widget)
        self.table_widget = QtWidgets.QTableWidget(0, 0)
        splitter.addWidget(self.table_widget)

        # Right widget (Image Viewer)
        self.image_viewer = ImageViewer()
        splitter.addWidget(self.image_viewer)

        self.main_layout.addWidget(splitter)
        
        self.table_settings_widgets = TableSettingsWidgets()

        self._create_table_size_editor()
        self._create_toolbar_widgets()
        self._create_toolbar()
        self._connect_to_image_viewer_signals()
        
    def set_table_detector_workspace(self, pdf_file_wrapper: PDFFileWrapper) -> None:
        """Create TableDetectorWorkspace (pdfplumber table tools) with given pdf file wrapper object
        and set the image wrapper object for it. Also, set the image for the image_viewer.
        """
        self.table_detector_workspace = TableDetectorWorkspace(pdf_file_wrapper)
        self.image_viewer.set_images(self.table_detector_workspace.set_pdf_file_image().pdf_file.image.image_bytes)

    def _create_toolbar(self):
        toolbar = QtWidgets.QToolBar("Table Capture Tools", self)
        self.addToolBar(QtCore.Qt.ToolBarArea.RightToolBarArea, toolbar)
        toolbar.setMovable(False)
        toolbar.addWidget(self.editing_tools_widget)
        toolbar.addSeparator()
        for w in self.table_settings_widgets.get_all_widgets():
            toolbar.addWidget(w)

    def __table_drawing_tool_button_clicked(self) -> None:
        if not self.table_drawing_tool_button.isChecked():
            # Prevent unchecking the button
            self.table_drawing_tool_button.setChecked(True)
        else:
            self.hand_tool_button.setChecked(False)

        if not self.table_size_widget_active:
            self._enable_table_size_editor()

        self.image_viewer.set_all_tabs_attr('drawing_enabled', True)

    def __hand_tool_button_clicked(self) -> None:
        if not self.hand_tool_button.isChecked():
            self.hand_tool_button.setChecked(True)
        else:
            self.table_drawing_tool_button.setChecked(False)

        if self.table_size_widget_active:
            self._enable_table_size_editor(False)

        self.image_viewer.set_all_tabs_attr('drawing_enabled', False)

    def __column_count_changed(self) -> None:
        self.image_viewer.set_all_tabs_attr('table_column_count', self.column_count_spinbox.value())

    def __row_count_changed(self) -> None:
        self.image_viewer.set_all_tabs_attr('table_row_count', self.row_count_spinbox.value())

    def _create_table_size_editor(self) -> None:
        self.table_size_widget = QtWidgets.QWidget()
        table_size_layout = QtWidgets.QVBoxLayout()

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        table_size_layout.addWidget(line)

        column_count_widget, self.column_count_spinbox = create_spinbox_with_label("Columns: ", 2, 2, 30)
        self.column_count_spinbox.valueChanged.connect(self.__column_count_changed)
        table_size_layout.addWidget(column_count_widget)

        row_count_widget, self.row_count_spinbox = create_spinbox_with_label("Rows: ", 3, 3, 50)
        self.row_count_spinbox.valueChanged.connect(self.__row_count_changed)
        table_size_layout.addWidget(row_count_widget)

        self.table_size_widget.setLayout(table_size_layout)
        self.table_size_widget_active = False

    def _enable_table_size_editor(
        self,
        enable: bool = True,
        col_count: int | None = None,
        row_count: int | None = None
    ) -> None:
        self.table_size_widget_active = enable
        if enable:
            self.editing_tools_layout.addWidget(self.table_size_widget)
            if is_all_not_none(col_count, row_count):
                self.column_count_spinbox.setValue(col_count)
                self.row_count_spinbox.setValue(row_count)
        else:
            self.editing_tools_layout.removeWidget(self.table_size_widget)
    
    def _create_toolbar_widgets(self) -> None:

        self.editing_tools_widget = QtWidgets.QWidget()
        self.editing_tools_layout = QtWidgets.QVBoxLayout()

        self.table_drawing_tool_button = QtWidgets.QPushButton("Table Creator")
        self.table_drawing_tool_button.setCheckable(True)
        self.table_drawing_tool_button.setChecked(False)
        self.table_drawing_tool_button.clicked.connect(self.__table_drawing_tool_button_clicked)
        self.editing_tools_layout.addWidget(self.table_drawing_tool_button)

        self.hand_tool_button = QtWidgets.QPushButton("Hand Tool")
        self.hand_tool_button.setCheckable(True)
        self.hand_tool_button.setChecked(True)
        self.hand_tool_button.clicked.connect(self.__hand_tool_button_clicked)
        self.editing_tools_layout.addWidget(self.hand_tool_button)

        self.editing_tools_widget.setLayout(self.editing_tools_layout)

    def _connect_to_image_viewer_signals(self) -> None:
        # TODO: Update signals
        self.image_viewer.newTable.connect(self.__new_table)
        self.image_viewer.tableUpdated.connect(self.__table_updated)
        self.image_viewer.tableDeleted.connect(self.__table_deleted)
        self.image_viewer.tableSelected.connect(self.__table_selected)
        self.image_viewer.tableDeselected.connect(self.__table_deselected)
        
    def _update_table_widget(self) -> None:
        self.table_widget.setColumnCount(max([len(table['vlines']) + 1 for table in self.tables]))
        self.table_widget.setRowCount(sum([len(table['hlines']) + 1 for table in self.tables]))
        
    def __new_table(self, page_index: int, table_obj: QTableF) -> None:
        self.tables.append(table_obj.get_data())
            
        # Add table
        self.table_detector_workspace.add_table(
            top_left=table_obj.get_data()['top_left'],
            bottom_right=table_obj.get_data()['bottom_right'],
            vlines=table_obj.get_data()['vlines'],
            hlines=table_obj.get_data()['hlines'],
            page_index=page_index
        )
        
        self._update_table_widget()

    def __table_updated(self, page_index: int, table_index: int, table_obj: QTableF) -> None:
        # Remove old table
        self.table_detector_workspace.remove_table(
            top_left=self.tables[table_index]['top_left'],
            bottom_right=self.tables[table_index]['bottom_right'],
            vlines=self.tables[table_index]['vlines'],
            hlines=self.tables[table_index]['hlines'],
            page_index=page_index
        )
        
        self.tables[table_index] = table_obj.get_data()
        
        # Add updated table
        self.table_detector_workspace.add_table(
            top_left=table_obj.get_data()['top_left'],
            bottom_right=table_obj.get_data()['bottom_right'],
            vlines=table_obj.get_data()['vlines'],
            hlines=table_obj.get_data()['hlines'],
            page_index=page_index
        )
        
        self._update_table_widget()

    def __table_deleted(self, page_index: int, table_index: int) -> None:
        self.table_detector_workspace.remove_table(
            top_left=self.tables[table_index]['top_left'],
            bottom_right=self.tables[table_index]['bottom_right'],
            vlines=self.tables[table_index]['vlines'],
            hlines=self.tables[table_index]['hlines'],
            page_index=page_index
        )
        self.tables.pop(table_index)
        self._update_table_widget()

    def __table_selected(self, table_index: int) -> None:
        col_count = len(self.tables[table_index]['vlines']) + 1
        row_count = len(self.tables[table_index]['hlines']) + 1
        self._enable_table_size_editor(True, col_count, row_count)

    def __table_deselected(self) -> None:
        self._enable_table_size_editor(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    editor = TableExtractor()
    editor.show()
    sys.exit(app.exec())
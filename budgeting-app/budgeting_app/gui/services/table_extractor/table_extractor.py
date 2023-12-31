import sys
from typing import Any, Callable
import logging

from PyQt6 import QtWidgets, QtCore

from budgeting_app.gui.utils.tools import (
    create_dropdown_with_label,
    create_spinbox_with_label,
    create_checkbox_with_label,
    ExpandableSpinBoxList
)
from budgeting_app.gui.services.table_extractor.image_tools import QTableF, Tools, PythonicTableData
from budgeting_app.gui.services.table_extractor.image_viewer import ImageViewer
from budgeting_app.gui.services.base import MainWindow, ServiceRequirement
from budgeting_app.pdf_table_reader.core.entities.models import ExplicitLineData, PDFFileWrapper
from budgeting_app.pdf_table_reader.core.usecases.table_detector_workspace import TableDetectorWorkspace, DEFAULT_TABLE_SETTINGS
from budgeting_app.utils.tools import is_all_not_none
from budgeting_app.utils.logging import CustomLoggerAdapter


class TableSettingsWidgets:
    table_detector_workspace: TableDetectorWorkspace
    _get_current_page_index: Callable[[], int]
    _get_table_settings: Callable[[], dict[str, Any]]
    _get_explicit_lines: Callable[[], list[ExplicitLineData]]
    
    strategy_allowed_values: list[str] = ["lines", "lines_strict", "text", "explicit"]
    
    # container widgets
    vertical_strategy_widget: QtWidgets.QWidget
    horizontal_strategy_widget: QtWidgets.QWidget
    snap_tolerance_widget: QtWidgets.QWidget
    snap_x_tolerance_widget: QtWidgets.QWidget
    snap_y_tolerance_widget: QtWidgets.QWidget
    join_tolerance_widget: QtWidgets.QWidget
    join_x_tolerance_widget: QtWidgets.QWidget
    join_y_tolerance_widget: QtWidgets.QWidget
    edge_min_length_widget: QtWidgets.QWidget
    min_words_vertical_widget: QtWidgets.QWidget
    min_words_horizontal_widget: QtWidgets.QWidget
    text_tolerance_widget: QtWidgets.QWidget
    text_x_tolerance_widget: QtWidgets.QWidget
    text_y_tolerance_widget: QtWidgets.QWidget
    intersection_tolerance_widget: QtWidgets.QWidget
    intersection_x_tolerance_widget: QtWidgets.QWidget
    intersection_y_tolerance_widget: QtWidgets.QWidget
    
    # special place for special widgets
    explicit_vertical_lines_cls: ExpandableSpinBoxList
    explicit_vertical_lines_widget: QtWidgets.QWidget
    explicit_horizontal_lines_cls: ExpandableSpinBoxList
    explicit_horizontal_lines_widget: QtWidgets.QWidget
    
    # value widgets
    vertical_strategy_cbox: QtWidgets.QComboBox
    horizontal_strategy_cbox: QtWidgets.QComboBox
    snap_tolerance_sbox: QtWidgets.QSpinBox
    snap_x_tolerance_sbox: QtWidgets.QSpinBox
    snap_y_tolerance_sbox: QtWidgets.QSpinBox
    join_tolerance_sbox: QtWidgets.QSpinBox
    join_x_tolerance_sbox: QtWidgets.QSpinBox
    join_y_tolerance_sbox: QtWidgets.QSpinBox
    edge_min_length_sbox: QtWidgets.QSpinBox
    min_words_vertical_sbox: QtWidgets.QSpinBox
    min_words_horizontal_sbox: QtWidgets.QSpinBox
    text_tolerance_sbox: QtWidgets.QSpinBox
    text_x_tolerance_sbox: QtWidgets.QSpinBox
    text_y_tolerance_sbox: QtWidgets.QSpinBox
    intersection_tolerance_sbox: QtWidgets.QSpinBox
    intersection_x_tolerance_sbox: QtWidgets.QSpinBox
    intersection_y_tolerance_sbox: QtWidgets.QSpinBox
    
    # checkboxes for applying settings acros all pages
    vertical_strategy_all_pages_checkbox: QtWidgets.QCheckBox
    horizontal_strategy_all_pages_checkbox: QtWidgets.QCheckBox
    
    def __init__(self) -> None:
        self.__vertical_strategy_set_up()
        self.__horizontal_strategy_set_up()
        self.__explicit_vertical_lines_set_up()
        self.__explicit_horizontal_lines_set_up()
        self.__snap_tolerance_set_up()
        self.__snap_x_tolerance_set_up()
        self.__snap_y_tolerance_set_up()
        self.__join_tolerance_set_up()
        self.__join_x_tolerance_set_up()
        self.__join_y_tolerance_set_up()
        self.__edge_min_length_set_up()
        self.__min_words_vertical_set_up()
        self.__min_words_horizontal_set_up()
        self.__text_tolerance_set_up()
        self.__text_x_tolerance_set_up()
        self.__text_y_tolerance_set_up()
        self.__intersection_tolerance_set_up()
        self.__intersection_x_tolerance_set_up()
        self.__intersection_y_tolerance_set_up()

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
            self.text_tolerance_widget,
            self.text_x_tolerance_widget,
            self.text_y_tolerance_widget,
            self.intersection_tolerance_widget,
            self.intersection_x_tolerance_widget,
            self.intersection_y_tolerance_widget
        ]

    def connect_signals(
        self,
        table_detector_workspace: TableDetectorWorkspace,
        _get_current_page_index: Callable[[], int],
    ) -> None:
        
        self.table_detector_workspace = table_detector_workspace
        self._get_current_page_index = _get_current_page_index
        self._get_table_settings = lambda: table_detector_workspace.pdf_file.pages[self._get_current_page_index()].table_settings
        self._get_explicit_lines = lambda: table_detector_workspace.pdf_file.pages[self._get_current_page_index()].explicit_lines
        
        self.__vertical_strategy_connect()
        self.__horizontal_strategy_connect()
        self.__explicit_vertical_lines_connect()
        self.__explicit_horizontal_lines_connect()
        self.__snap_tolerance_connect()
        self.__snap_x_tolerance_connect()
        self.__snap_y_tolerance_connect()
        self.__join_tolerance_connect()
        self.__join_x_tolerance_connect()
        self.__join_y_tolerance_connect()
        self.__edge_min_length_connect()
        self.__min_words_vertical_connect()
        self.__min_words_horizontal_connect()
        self.__text_tolerance_connect()
        self.__text_x_tolerance_connect()
        self.__text_y_tolerance_connect()
        self.__intersection_tolerance_connect()
        self.__intersection_x_tolerance_connect()
        self.__intersection_y_tolerance_connect()
        
    def from_table_settings(self) -> None:
        for key in [
            'vertical_strategy',
            'horizontal_strategy'
        ]:
            QtWidgets.QComboBox.setCurrentIndex(
                getattr(self, f'{key}_cbox'),
                self.strategy_allowed_values.index(self._get_table_settings()[key])
            )
        
        for key in [
            'snap_tolerance',
            'snap_x_tolerance',
            'snap_y_tolerance',
            'join_tolerance',
            'join_x_tolerance',
            'join_y_tolerance',
            'edge_min_length',
            'min_words_vertical',
            'min_words_horizontal',
            'text_tolerance',
            'text_x_tolerance',
            'text_y_tolerance',
            'intersection_tolerance',
            'intersection_x_tolerance',
            'intersection_y_tolerance'
        ]:
            QtWidgets.QSpinBox.setValue(
                getattr(self, f'{key}_sbox'),
                self._get_table_settings()[key]
            )
        
        for orientation in ['vertical', 'horizontal']:
            ExpandableSpinBoxList.values_from_list(
                getattr(self, f'explicit_{orientation}_lines_cls'),
                [
                    {'uuid': line.uuid, 'value': line.value} for line in self._get_explicit_lines()
                    if line.orientation == orientation and not line.is_part_of_table
                ]
            )
        
    def __vertical_strategy_set_up(self) -> None:
        
        self.vertical_strategy_widget, self.vertical_strategy_cbox = create_dropdown_with_label(
            "Vertical strategy:",
            self.strategy_allowed_values,
            self.strategy_allowed_values.index(DEFAULT_TABLE_SETTINGS.get('vertical_strategy'))
        )
        vertical_strategy_all_pages_checkbox_conainer, \
            self.vertical_strategy_all_pages_checkbox = create_checkbox_with_label(_label='Apply to all pages')
        self.vertical_strategy_widget.layout().addWidget(vertical_strategy_all_pages_checkbox_conainer)
    
    def __vertical_strategy_connect(self) -> None:
        self.vertical_strategy_cbox.currentTextChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all' if self.vertical_strategy_all_pages_checkbox.isChecked() else self._get_current_page_index(),
                'vertical_strategy',
                self.vertical_strategy_cbox.currentText()
            )
        )
        self.vertical_strategy_all_pages_checkbox.clicked.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'vertical_strategy',
                self.vertical_strategy_cbox.currentText()
            ) if self.vertical_strategy_all_pages_checkbox.isChecked() else None
        )
        
    def __horizontal_strategy_set_up(self) -> None:
        self.horizontal_strategy_widget, self.horizontal_strategy_cbox = create_dropdown_with_label(
            "Horizontal strategy:",
            self.strategy_allowed_values,
            self.strategy_allowed_values.index(DEFAULT_TABLE_SETTINGS.get('horizontal_strategy'))
        )
        horizontal_strategy_all_pages_checkbox_conainer, \
            self.horizontal_strategy_all_pages_checkbox = create_checkbox_with_label(_label='Apply to all pages')
        self.horizontal_strategy_widget.layout().addWidget(horizontal_strategy_all_pages_checkbox_conainer)
    
    def __horizontal_strategy_connect(self) -> None:
        self.horizontal_strategy_cbox.currentTextChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all' if self.horizontal_strategy_all_pages_checkbox.isChecked() else self._get_current_page_index(),
                'horizontal_strategy',
                self.horizontal_strategy_cbox.currentText()
            )
        )
        self.horizontal_strategy_all_pages_checkbox.clicked.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'horizontal_strategy',
                self.horizontal_strategy_cbox.currentText()
            ) if self.horizontal_strategy_all_pages_checkbox.isChecked() else None
        )
        
    def __explicit_vertical_lines_set_up(self) -> None:
        self.explicit_vertical_lines_cls = ExpandableSpinBoxList(
            button_text="Add vertical line",
            _min=0,
        )
        self.explicit_vertical_lines_widget = self.explicit_vertical_lines_cls.main_container
    
    def __explicit_vertical_lines_connect(self) -> None:
        self.explicit_vertical_lines_cls.add_value = lambda val: self.table_detector_workspace.add_line(val, 'vertical', self._get_current_page_index())[1]
        self.explicit_vertical_lines_cls.update_value = lambda uuid, val: self.table_detector_workspace.update_line_pos(uuid, val, self._get_current_page_index())
        self.explicit_vertical_lines_cls.remove_value = lambda uuid: self.table_detector_workspace.remove_line(uuid, self._get_current_page_index())
    
    def __explicit_horizontal_lines_set_up(self) -> None:
        self.explicit_horizontal_lines_cls = ExpandableSpinBoxList(
            button_text="Add horizontal line",
            _min=0,
        )
        self.explicit_horizontal_lines_widget = self.explicit_horizontal_lines_cls.main_container
    
    def __explicit_horizontal_lines_connect(self) -> None:
        self.explicit_horizontal_lines_cls.add_value = lambda val: self.table_detector_workspace.add_line(val, 'horizontal', self._get_current_page_index())[1]
        self.explicit_horizontal_lines_cls.update_value = lambda uuid, val: self.table_detector_workspace.update_line_pos(uuid, val, self._get_current_page_index())
        self.explicit_horizontal_lines_cls.remove_value = lambda uuid: self.table_detector_workspace.remove_line(uuid, self._get_current_page_index())
    
    def __snap_tolerance_set_up(self) -> None:
        self.snap_tolerance_widget, self.snap_tolerance_sbox = create_spinbox_with_label(
            "Snap tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('snap_tolerance')
        )
    
    def __snap_tolerance_connect(self) -> None:
        self.snap_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'snap_tolerance',
                self.snap_tolerance_sbox.value()
            )
        )
        
    def __snap_x_tolerance_set_up(self) -> None:
        self.snap_x_tolerance_widget, self.snap_x_tolerance_sbox = create_spinbox_with_label(
            "Snap x tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('snap_x_tolerance')
        )
    
    def __snap_x_tolerance_connect(self) -> None:
        self.snap_x_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'snap_x_tolerance',
                self.snap_x_tolerance_sbox.value()
            )
        )
        
    def __snap_y_tolerance_set_up(self) -> None:
        self.snap_y_tolerance_widget, self.snap_y_tolerance_sbox = create_spinbox_with_label(
            "Snap y tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('snap_y_tolerance')
        )
    
    def __snap_y_tolerance_connect(self) -> None:
        self.snap_y_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'snap_y_tolerance',
                self.snap_y_tolerance_sbox.value()
            )
        )
        
    def __join_tolerance_set_up(self) -> None:
        self.join_tolerance_widget, self.join_tolerance_sbox = create_spinbox_with_label(
            "Join tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('join_tolerance')
        )
    
    def __join_tolerance_connect(self) -> None:
        self.join_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'join_tolerance',
                self.join_tolerance_sbox.value()
            )
        )
        
    def __join_x_tolerance_set_up(self) -> None:
        self.join_x_tolerance_widget, self.join_x_tolerance_sbox = create_spinbox_with_label(
            "Join x tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('join_x_tolerance')
        )
    
    def __join_x_tolerance_connect(self) -> None:
        self.join_x_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'join_x_tolerance',
                self.join_x_tolerance_sbox.value()
            )
        )
        
    def __join_y_tolerance_set_up(self) -> None:
        self.join_y_tolerance_widget, self.join_y_tolerance_sbox = create_spinbox_with_label(
            "Join y tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('join_y_tolerance')
        )
    
    def __join_y_tolerance_connect(self) -> None:
        self.join_y_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'join_y_tolerance',
                self.join_y_tolerance_sbox.value()
            )
        )
        
    def __edge_min_length_set_up(self) -> None:
        self.edge_min_length_widget, self.edge_min_length_sbox = create_spinbox_with_label(
            "Edge min length: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('edge_min_length')
        )
    
    def __edge_min_length_connect(self) -> None:
        self.edge_min_length_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'edge_min_length',
                self.edge_min_length_sbox.value()
            )
        )
        
    def __min_words_vertical_set_up(self) -> None:
        self.min_words_vertical_widget, self.min_words_vertical_sbox = create_spinbox_with_label(
            "Min words vertical: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('min_words_vertical')
        )
    
    def __min_words_vertical_connect(self) -> None:
        self.min_words_vertical_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'min_words_vertical',
                self.min_words_vertical_sbox.value()
            )
        )
        
    def __min_words_horizontal_set_up(self) -> None:
        self.min_words_horizontal_widget, self.min_words_horizontal_sbox = create_spinbox_with_label(
            "Min words horizontal: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('min_words_horizontal')
        )
    
    def __min_words_horizontal_connect(self) -> None:
        self.min_words_horizontal_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'min_words_horizontal',
                self.min_words_horizontal_sbox.value()
            )
        )

    def __text_tolerance_set_up(self) -> None:
        self.text_tolerance_widget, self.text_tolerance_sbox = create_spinbox_with_label(
            "Text tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('text_tolerance', 3)
        )
        
    def __text_tolerance_connect(self) -> None:
        self.text_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'text_tolerance',
                self.text_tolerance_sbox.value()
            )
        )
    
    def __text_x_tolerance_set_up(self) -> None:
        self.text_x_tolerance_widget, self.text_x_tolerance_sbox = create_spinbox_with_label(
            "Text x tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('text_x_tolerance', 3)
        )
        
    def __text_x_tolerance_connect(self) -> None:
        self.text_x_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'text_x_tolerance',
                self.text_x_tolerance_sbox.value()
            )
        )
    
    def __text_y_tolerance_set_up(self) -> None:
        self.text_y_tolerance_widget, self.text_y_tolerance_sbox = create_spinbox_with_label(
            "Text y tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('text_y_tolerance')
        )
        
    def __text_y_tolerance_connect(self) -> None:
        self.text_y_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'text_y_tolerance',
                self.text_y_tolerance_sbox.value()
            )
        )
    
    def __intersection_tolerance_set_up(self) -> None:
        self.intersection_tolerance_widget, self.intersection_tolerance_sbox = create_spinbox_with_label(
            "Intersection tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('intersection_tolerance')
        )
        
    def __intersection_tolerance_connect(self) -> None:
        self.intersection_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'intersection_tolerance',
                self.intersection_tolerance_sbox.value()
            )
        )
    
    def __intersection_x_tolerance_set_up(self) -> None:
        self.intersection_x_tolerance_widget, self.intersection_x_tolerance_sbox = create_spinbox_with_label(
            "Intersection x tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('intersection_x_tolerance')
        )
        
    def __intersection_x_tolerance_connect(self) -> None:
        self.intersection_x_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'intersection_x_tolerance',
                self.intersection_x_tolerance_sbox.value()
            )
        )
    
    def __intersection_y_tolerance_set_up(self) -> None:
        self.intersection_y_tolerance_widget, self.intersection_y_tolerance_sbox = create_spinbox_with_label(
            "Intersection y tolerance: ",
            0,
            DEFAULT_TABLE_SETTINGS.get('intersection_y_tolerance')
        )
        
    def __intersection_y_tolerance_connect(self) -> None:
        self.intersection_y_tolerance_sbox.valueChanged.connect(
            lambda: self.table_detector_workspace.set_table_settings_val(
                'all',
                'intersection_y_tolerance',
                self.intersection_y_tolerance_sbox.value()
            )
        )


class TableExtractor(MainWindow):

    # editing_tools_widget hosts tool buttons and optionally table_size_widget
    editing_tools_widget: QtWidgets.QWidget
    editing_tools_layout: QtWidgets.QVBoxLayout
    
    find_tables_button: QtWidgets.QPushButton
    
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
    
    logger: logging.LoggerAdapter

    def __init__(self, parent: Any | None = None):
        super().__init__(parent)
        self.setWindowTitle("Budgeting App - Table Extractor")
        # self.setGeometry(self.window_default_geometry)
        
        self.logger = CustomLoggerAdapter.getLogger('gui', className='TableExtractor')
        self.logger.info('Initialising TableExtractor.')

        self.tables = []
        self.service_requirements = [
            ServiceRequirement(
                attr_name='set_table_detector_workspace',
                is_callable=True,
                properties=['pdf_file_wrapper']
            )
        ]

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
        
        # set up TableDetectorWorkspace with given PDFFileWrapper
        self.logger.debug('Setting up TableDetectorWorkspace with pdf_file_wrapper=....')
        self.table_detector_workspace = TableDetectorWorkspace(pdf_file_wrapper)
        
        # set images for ImageViewer tabs
        self.logger.debug('Setting images for ImageViewer tabs.')
        self.image_viewer.set_images(
            self.table_detector_workspace.set_pdf_file_image().image_bytes,
            self.table_drawing_tool_button.isChecked()
        )

        # connect appropriate TableDetectorWorkspace methods to TableSettingsWidgets' widgets signals
        self.logger.debug('Connecting TableDetectorWorkspace to TableSettingsWidgets.')
        self.table_settings_widgets.connect_signals(self.table_detector_workspace, lambda: self.image_viewer.current_tab)
        
        # pull data from the table settings and update values in the toolbox accordingly when the tab is changed
        self.logger.debug('Connecting TableSettingsWidgets.from_table_settings method to ImageViewer.tab_widget.currentChanged signal.')
        self.image_viewer.tab_widget.currentChanged.connect(self.table_settings_widgets.from_table_settings)
        
        # update table widget automatically when the pages are loaded
        self._update_table_widget()
        
        # connect an observer function, ImageViewer.update_image, to each relevant
        # page's settings dictionary (it will not be triggered for the default settings)
        image_page_indices = self.table_detector_workspace.pdf_file.image.page_indices
        image_page_indices = image_page_indices if image_page_indices != 'all' else [*range(len(self.table_detector_workspace.pdf_file.pages))]
        for tab_index, page_index in enumerate(image_page_indices):
            self.logger.debug(f'TableExtractor.set_table_detector_workspace: tab_index={tab_index}, page_index={page_index}')
            self.table_detector_workspace.pdf_file.pages[page_index].table_settings.add_callback(self.__table_settings_updated)
            
    def __table_settings_updated(self, key: str | None = None, val: Any | None = None) -> None:
        if not self.find_tables_button.isEnabled():
            self.find_tables_button.setEnabled(True)

    def _create_toolbar(self):
        toolbar = QtWidgets.QToolBar("Table Capture Tools", self)
        self.addToolBar(QtCore.Qt.ToolBarArea.RightToolBarArea, toolbar)
        toolbar.setMovable(False)
        toolbar.addWidget(self.editing_tools_widget)
        toolbar.addSeparator()
        for w in self.table_settings_widgets.get_all_widgets():
            toolbar.addWidget(w)

    def __find_tables_button_clicked(self) -> None:
        self.image_viewer.update_image(
            self.image_viewer.current_tab,
            self.table_detector_workspace.image_bytes[self.image_viewer.current_tab]
        )
        self._update_table_widget()
        self.find_tables_button.setEnabled(False)

    def __table_drawing_tool_button_clicked(self) -> None:
        if not self.table_drawing_tool_button.isChecked():
            # Prevent unchecking the button
            self.table_drawing_tool_button.setChecked(True)
            self.logger.debug('Tool set to table drawing.')
        else:
            self.hand_tool_button.setChecked(False)

        if not self.table_size_widget_active:
            self._enable_table_size_editor()

        self.image_viewer.set_all_tabs_attr('drawing_enabled', True)

    def __hand_tool_button_clicked(self) -> None:
        if not self.hand_tool_button.isChecked():
            self.hand_tool_button.setChecked(True)
            self.logger.debug('Tool set to hand.')
        else:
            self.table_drawing_tool_button.setChecked(False)

        if self.table_size_widget_active:
            self._enable_table_size_editor(False)

        self.image_viewer.set_all_tabs_attr('drawing_enabled', False)

    def __column_count_changed(self) -> None:
        self.logger.debug(f'Column cound changed to {self.column_count_spinbox.value()}')
        self.image_viewer.set_all_tabs_attr('table_column_count', self.column_count_spinbox.value())

    def __row_count_changed(self) -> None:
        self.logger.debug(f'Row cound changed to {self.row_count_spinbox.value()}')
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

        self.find_tables_button = QtWidgets.QPushButton("Find Tables")
        self.find_tables_button.setEnabled(False)
        self.find_tables_button.clicked.connect(self.__find_tables_button_clicked)
        self.editing_tools_layout.addWidget(self.find_tables_button)

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
        self.image_viewer.newTable.connect(self.__new_table)
        self.image_viewer.tableUpdated.connect(self.__table_updated)
        self.image_viewer.tableDeleted.connect(self.__table_deleted)
        self.image_viewer.tableSelected.connect(self.__table_selected)
        self.image_viewer.tableDeselected.connect(self.__table_deselected)
        
    def _update_table_widget(self) -> None:
        """Update the table widget with text from all tables found across all pages. The data are
        collected not only from the page image that is currently viewed.
        """
        
        page_indices = [*range(len(self.table_detector_workspace.pdf_file.pages))] \
            if self.table_detector_workspace.pdf_file.image.page_indices == 'all' \
            else self.table_detector_workspace.pdf_file.image.page_indices
        self.logger.debug(f'Collecting table text data from pages: {page_indices}')
        
        tables_content = self.table_detector_workspace.get_tables_text(page_indices)
        tables_content = [row for table in tables_content for row in table]
        self.logger.debug(f'Got {len(tables_content)} rows of data.')
        
        self.table_widget.setColumnCount(max([len(table) for table in tables_content]))
        self.table_widget.setRowCount(len(tables_content))
        
        for row_index, row_data in enumerate(tables_content):
            for col_index, cell_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(cell_data))
                self.table_widget.setItem(row_index, col_index, item)
        
    def __new_table(self, table_obj: QTableF) -> None:
        
        page_index = self.image_viewer.current_tab
        
        self.logger.info(f'page_index={page_index}, table_obj={table_obj}')
        self.tables.append(table_obj.get_data())
            
        # Add table
        self.table_detector_workspace.add_table(
            top_left=table_obj.get_data()['top_left'],
            bottom_right=table_obj.get_data()['bottom_right'],
            vlines=table_obj.get_data()['vlines'],
            hlines=table_obj.get_data()['hlines'],
            page_index=page_index
        )
        self.logger.info(f'table_settings={self.table_detector_workspace.get_table_settings(page_index)}')

    def __table_updated(self, table_index: int, table_obj: QTableF) -> None:
        page_index = self.image_viewer.current_tab
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

    def __table_deleted(self, table_index: int) -> None:
        page_index = self.image_viewer.current_tab
        self.table_detector_workspace.remove_table(
            top_left=self.tables[table_index]['top_left'],
            bottom_right=self.tables[table_index]['bottom_right'],
            vlines=self.tables[table_index]['vlines'],
            hlines=self.tables[table_index]['hlines'],
            page_index=page_index
        )
        self.tables.pop(table_index)

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
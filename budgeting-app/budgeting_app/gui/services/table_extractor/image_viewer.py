from typing import Any
from PyQt6 import QtWidgets, QtCore, QtGui

from budgeting_app.gui.services.table_extractor.image_tools import (
    QTableF,
    AddMode,
    TableInfo,
    DrawingSettings,
    ImageData,
    TableDrawingTool,
    SelectedTable
)
from budgeting_app.utils.tools import is_all_not_none


class Canvas(QtWidgets.QWidget):
    drawing_enabled: bool
    image_data: ImageData
    
    offset_x: float
    offset_y: float
    most_recent_scale_ratio: float
    
    start_pos: QtCore.QPointF | None
    end_pos: QtCore.QPointF | None
    
    tables: list[QTableF]
    table_info: TableInfo

    newTable = QtCore.pyqtSignal(QTableF)
    """
    Args:\n
        `table (QTableF)` - new table object\n
    """
    
    tableUpdated = QtCore.pyqtSignal(int, QTableF)
    """
    Args:\n
        `table_index (int)` - index of the updated table\n
        `table (QTableF)` - updated table object\n
    """

    tableDeleted = QtCore.pyqtSignal(int)
    """
    Args:\n
        `table_index (int)` - index of the deleted table\n
    """
    
    tableSelected = QtCore.pyqtSignal(int)
    """
    Args:\n
        `table_index (int)` - index of the selected table\n
    """
    
    tableDeselected = QtCore.pyqtSignal()

    def __init__(self, image_bytes: bytes, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.is_drawing_enabled = True
        self.table_info = TableInfo(table_drawing_settings=DrawingSettings())
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.start_pos = None
        self.end_pos = None
        self.tables = []
        self.most_recent_scale_ratio = 1.0
        
        self.__set_image(image_bytes)
    
    @property
    def image_bytes(self) -> bytes | None:
        if self.image_data is not None:
            img_bytes = QtCore.QByteArray()
            device = QtCore.QIODevice(img_bytes)
            device.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
            self.image_data.original_image.save(device, format='PNG')
            return img_bytes.data()
        
    @property
    def drawing_enabled(self) -> bool:
        return self.is_drawing_enabled
    
    @property
    def col_add_mode(self) -> AddMode:
        return self.table_info.table_drawing_settings.col_add_mode
    
    @property
    def row_add_mode(self) -> AddMode:
        return self.table_info.table_drawing_settings.row_add_mode
    
    @property
    def table_column_count(self) -> int:
        return self.table_info.table_drawing_settings.col_count
    
    @property
    def table_row_count(self) -> int:
        return self.table_info.table_drawing_settings.row_count
    
    @image_bytes.setter
    def image_bytes(self, val: bytes) -> None:
        self.__set_image(val)
    
    @drawing_enabled.setter
    def drawing_enabled(self, val: bool) -> None:
        self.is_drawing_enabled = val
        if self.is_drawing_enabled:
            # clear out the vars - they only make sense when using hand tool
            self.table_info.selected_table = None
            self.table_info.selected_element = None
            self.update()
            
    @col_add_mode.setter
    def col_add_mode(self, val: AddMode) -> None:
        self.table_info.table_drawing_settings.col_add_mode = val
    
    @row_add_mode.setter
    def row_add_mode(self, val: AddMode) -> None:
        self.table_info.table_drawing_settings.row_add_mode = val
    
    @table_column_count.setter
    def table_column_count(self, val: int) -> None:
        self.table_info.table_drawing_settings.col_count = val
        
        if self.table_info.selected_table is not None:
            # Update number of column in existing table
            self.tables[self.table_info.selected_table.index] = TableDrawingTool.update_column_count(
                self.tables[self.table_info.selected_table.index],
                self.table_info.table_drawing_settings.col_count,
                self.table_info.table_drawing_settings.col_add_mode
            )
            self.update()
    
    @table_row_count.setter
    def table_row_count(self, val: int) -> None:
        self.table_info.table_drawing_settings.row_count = val
        
        if self.table_info.selected_table is not None:
            self.tables[self.table_info.selected_table.index] = TableDrawingTool.update_row_count(
                self.tables[self.table_info.selected_table.index],
                self.table_info.table_drawing_settings.row_count,
                self.table_info.table_drawing_settings.row_add_mode
            )
            self.update()
    
    def __set_image(self, img_bytes: bytes) -> None:
        
        # Get PIL.Image object from bytes
        img = QtGui.QImage().fromData(QtCore.QByteArray(img_bytes))
    
        # Add ImageData object to the self.images_data list
        self.image_data = ImageData(
            original_image=img,
            current_scaled_image=img,
            current_origin_pos=QtCore.QPointF(0.0, 0.0)
        )
        
        self.update_image_origin_pos()
        self.update()
            
    def update_image_origin_pos(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: Image origin displacement `(dx, dy)`
        """
        # New postion of the image origin
        x = (self.width() - self.image_data.current_scaled_image.width()) / 2 + self.offset_x
        y = (self.height() - self.image_data.current_scaled_image.height()) / 2 + self.offset_y
        
        # Image origin displacement
        dx = x - self.image_data.current_origin_pos.x()
        dy = y - self.image_data.current_origin_pos.y()
        
        self.image_data.current_origin_pos = QtCore.QPointF(x, y)
        
        return dx, dy

    def wheelEvent(self, event: QtGui.QWheelEvent):
        # Update image_data.current_size from event
        current_image_size = self.image_data.current_scaled_image.size()
        if event.angleDelta().y() > 0:
            current_image_size *= 1.1
        else:
            current_image_size /= 1.1
        
        # Update image from the 
        self.image_data.current_scaled_image = self.image_data.original_image.scaled(current_image_size, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.update_image_origin_pos()
        self.tables, self.most_recent_scale_ratio = TableDrawingTool.update_tables_scale(self.tables, self.image_data, self.most_recent_scale_ratio)
            
        self.update()
        
    def resizeEvent(self, _: QtGui.QResizeEvent) -> None:
        dx, dy = self.update_image_origin_pos()
        self.tables = TableDrawingTool.move_tables(self.tables, dx, dy)
        self.tables, self.most_recent_scale_ratio = TableDrawingTool.update_tables_scale(self.tables, self.image_data, self.most_recent_scale_ratio)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.start_pos = event.position()
            self.end_pos = event.position()

            if not self.is_drawing_enabled and self.table_info.selected_table is not None:
                # That only runs when the selected tool is HAND_TOOL and we already have a table that is selected.
                # I want to 'register' the element on press so that it can be updated when the mouse button is pressed
                # and the coursor is being moved.
                self.table_info = TableDrawingTool.get_table_element_by_handle(event.position(), self.table_info)
        
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:

            if not self.is_drawing_enabled:

                if self.table_info.selected_table is None:

                    dx = event.position().x() - self.end_pos.x()
                    dy = event.position().y() - self.end_pos.y()
                    self.offset_x += dx
                    self.offset_y += dy
                    self.tables = TableDrawingTool.move_tables(self.tables, dx, dy)
                    self.image_data.current_origin_pos += QtCore.QPointF(dx, dy)

                elif self.table_info.selected_element is not None:
                    # if we selected a table and the mouse was clicked over one on the table element's handles,
                    # we want to move that element accordingly
                    self.tables[self.table_info.selected_table.index] = TableDrawingTool.update_table_element(
                        event.position(),
                        self.table_info,
                    )

            self.end_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:

            if self.is_drawing_enabled \
                and is_all_not_none(self.start_pos, self.table_info.table_drawing_settings.col_count, self.table_info.table_drawing_settings.row_count):
                    # If the button was released when using TABLE_DRAWING_TOOL add a new table to the list
                    new_table = TableDrawingTool.get_table(
                        self.start_pos,
                        event.position(),
                        self.table_info.table_drawing_settings.col_count,
                        self.table_info.table_drawing_settings.row_count
                    )
                    self.tables.append(new_table)
                    self.newTable.emit(new_table)
                    
            elif not self.is_drawing_enabled:
                # If the button was released when using HAND_TOOL the behavior is different when we're holding
                # an element of the table or not
                if self.table_info.selected_table is None:
                    # when we're not holding any element verify if we're clocking on the table or not
                    table_index = TableDrawingTool.get_table_by_line(event.position(), self.tables)
                    if table_index is not None:
                        self.table_info.selected_table = SelectedTable(
                            index=table_index,
                            table=self.tables[table_index]
                        )
                        self.table_info.table_drawing_settings.col_count = len(self.tables[table_index].vertical_separators) + 1
                        self.table_info.table_drawing_settings.row_count = len(self.tables[table_index].horizontal_separators) + 1
                        self.tableSelected.emit(table_index)
                    else:
                        self.tableDeselected.emit()
                else:
                    # when we were holding an element just set selected_table_element to None
                    self.table_info.selected_element = None

            self.update()

    def paintEvent(self, _: QtGui.QPaintEvent):
            
        painter = QtGui.QPainter(self)
        painter.drawImage(self.image_data.current_origin_pos, self.image_data.current_scaled_image)

        if not self.is_drawing_enabled and self.table_info.selected_table is not None:
            TableDrawingTool.draw_selection_handles(painter, self.tables[self.table_info.selected_table.index])
        elif self.is_drawing_enabled and is_all_not_none(self.start_pos, self.end_pos):
            TableDrawingTool.draw(
                painter=painter,
                start_qpoint=self.start_pos,
                end_qpoint=self.end_pos,
                col_count=self.table_info.table_drawing_settings.col_count,
                row_count=self.table_info.table_drawing_settings.row_count
            )

        TableDrawingTool.draw_all(painter, self.tables)
            
            
class ImageViewer(QtWidgets.QWidget):
    tab_layout: QtWidgets.QVBoxLayout
    tab_widget: QtWidgets.QTabWidget
    tabs: list[Canvas]
    
    newTable = QtCore.pyqtSignal(int, QTableF)
    """
    Args:\n
        `page_index (int)` - index of the page where the table is created\n
        `table (QTableF)` - new table object\n
    """
    
    tableUpdated = QtCore.pyqtSignal(int, int, QTableF)
    """
    Args:\n
        `page_index (int)` - index of the page where the table is updated\n
        `table_index (int)` - index of the updated table\n
        `table (QTableF)` - updated table object\n
    """

    tableDeleted = QtCore.pyqtSignal(int, int)
    """
    Args:\n
        `page_index (int)` - index of the page where the table is deleted\n
        `table_index (int)` - index of the deleted table\n
    """
    
    tableSelected = QtCore.pyqtSignal(int)
    """
    Args:\n
        `table_index (int)` - index of the selected table\n
    """
    
    tableDeselected = QtCore.pyqtSignal()
    
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super(QtWidgets.QWidget, self).__init__(parent)
        
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        
        # Initialize tab screen
        self.tab_widget = QtWidgets.QTabWidget()
        # self.tab_widget.resize(300, 200)
  
        # Add tabs to widget
        self.tab_layout.addWidget(self.tab_widget)
        self.setLayout(self.tab_layout)
        
        # Filter for properties (getters and setters) in Canvas class
        self.canvas_attrs = [attr for attr in dir(Canvas) if isinstance(getattr(Canvas, attr, None), property)]
        
        self.tabs = []
        
    def set_images(self, image_bytes_list: list[bytes]) -> None:
        
        for i, img_bytes in enumerate(image_bytes_list):
            tab = Canvas(img_bytes)
            self.tab_widget.addTab(tab, str(i))
            self.tabs.append(tab)
            
    def set_tab_attr(self, tab_index: int, attr_name: str, attr_value: Any) -> None:
        if attr_name in self.canvas_attrs:
            setattr(self.tabs[tab_index], attr_name, attr_value)
        else:
            raise ValueError(f'{attr_name} is not a setter of class Canvas.')
    
    def set_all_tabs_attr(self, attr_name: str, attr_value: Any) -> None:
        if attr_name in self.canvas_attrs:
            for tab in self.tabs:
                setattr(tab, attr_name, attr_value)
        else:
            raise ValueError(f'{attr_name} is not a setter of class Canvas.')
    
    def get_tab_property(self, tab_index: int, attr_name: str) -> Any:
        if attr_name in self.canvas_attrs:
            return getattr(self.tabs[tab_index], attr_name)
        else:
            raise ValueError(f'{attr_name} is not a getter of class Canvas.')

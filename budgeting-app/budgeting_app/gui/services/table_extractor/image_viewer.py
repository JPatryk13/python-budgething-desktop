import logging
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
from budgeting_app.utils.logging import CustomLoggerAdapter
from budgeting_app.utils.tools import is_all_not_none


class Canvas(QtWidgets.QWidget):
    drawing_enabled: bool
    image_data: ImageData
    is_drawing_enabled: bool
    
    offset_x: float
    offset_y: float
    most_recent_scale_ratio: float
    
    start_pos: QtCore.QPointF | None
    end_pos: QtCore.QPointF | None
    
    tables: list[QTableF]
    table_info: TableInfo
    
    logger: logging.LoggerAdapter

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

    def __init__(self, image_bytes: bytes, is_drawing_enabled: bool, parent: QtWidgets.QWidget | None = None):
        self.logger = CustomLoggerAdapter.getLogger('gui', className='Canvas')
        self.logger.debug('Initializing Canvas with image_bytes=....')
        
        super().__init__(parent)
        self.is_drawing_enabled = is_drawing_enabled
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
        self.logger.debug('Setting image from img_bytes.')
        
        # Get PIL.Image object from bytes
        img = QtGui.QImage().fromData(QtCore.QByteArray(img_bytes))
        
        if getattr(self, 'image_data', None) is None:
            self.logger.debug(f'image_data doesn\'t exist. Creating new image_data with {img} and current_origin_pos={QtCore.QPointF(0.0, 0.0)}')
            # Add ImageData object to the self.images_data list
            self.image_data = ImageData(
                original_image=img,
                current_scaled_image=img,
                current_origin_pos=QtCore.QPointF(0.0, 0.0)
            )
            self.update_image_origin_pos()
            
        else:
            self.logger.debug('image_data already exists.')
            
            # Update image content but keep the scale and origin position the same
            self.logger.debug('Updating image_data.original_image value.')
            self.image_data.original_image = img
            self.logger.debug(f'resizing {img} with image_data.current_scaled_image={self.image_data.current_scaled_image.size()} and updating image_data.current_scaled_image.')
            self.image_data.current_scaled_image = img.scaled(self.image_data.current_scaled_image.size())
            
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
        
        self.logger.debug(f'Updating image origin position from {self.image_data.current_origin_pos} to {QtCore.QPointF(x, y)}.')
        self.image_data.current_origin_pos = QtCore.QPointF(x, y)
        
        self.logger.debug(f'Returning image origin displacement: dx={dx}, dy={dy}')
        return dx, dy

    def wheelEvent(self, event: QtGui.QWheelEvent):
        # Update image_data.current_size from event
        
        self.logger.debug(f'Got QtGui.QWheelEvent with angle delta y = {event.angleDelta().y()}')
        
        current_image_size = self.image_data.current_scaled_image.size()
        if event.angleDelta().y() > 0:
            current_image_size *= 1.1
        else:
            current_image_size /= 1.1
            
        self.logger.debug(f'Updating image size from {self.image_data.current_scaled_image.size()} to {current_image_size}')
        
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
            
            self.logger.debug(f'Triggered with event.position={event.position()}')

            self.logger.debug(f'self.is_drawing_enabled={self.is_drawing_enabled}')
            if not self.is_drawing_enabled:
                self.logger.debug(f'self.table_info.selected_table={self.table_info.selected_table}')
                # drawing is disabled
                if self.table_info.selected_table is None:
                    # no table is selected - adjust position of the image based on the coursor movement?
                    self.logger.debug(f'event.position={event.position()}')
                    dx = event.position().x() - self.end_pos.x()
                    dy = event.position().y() - self.end_pos.y()
                    self.logger.debug(f'dx={dx}, dy={dy}')
                    self.offset_x += dx
                    self.offset_y += dy
                    self.logger.debug(f'offset_x={self.offset_x}, offset_y={self.offset_y}')
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
                    # when we're not holding any element verify if we're clicking on the table or not
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
                    
            

            self.end_pos = None
            self.start_pos = None
            
            self.update()

    def paintEvent(self, _: QtGui.QPaintEvent):
            
        painter = QtGui.QPainter(self)
        painter.drawImage(self.image_data.current_origin_pos, self.image_data.current_scaled_image)

        if self.is_drawing_enabled:
            # drawing is enabled
            if is_all_not_none(self.start_pos, self.end_pos):
                # table is being drawn
                TableDrawingTool.draw(
                    painter=painter,
                    start_qpoint=self.start_pos,
                    end_qpoint=self.end_pos,
                    col_count=self.table_info.table_drawing_settings.col_count,
                    row_count=self.table_info.table_drawing_settings.row_count
                )
        else:
            # drawing is disabled
            if self.table_info.selected_table is not None:
                # table is selected
                TableDrawingTool.draw_selection_handles(painter, self.tables[self.table_info.selected_table.index])

        # draw existing tables
        TableDrawingTool.draw_all(painter, self.tables)
            
            
class ImageViewer(QtWidgets.QWidget):
    tab_layout: QtWidgets.QVBoxLayout
    tab_widget: QtWidgets.QTabWidget
    tabs: list[Canvas]
    
    logger: logging.LoggerAdapter
    
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
    
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        
        self.logger = CustomLoggerAdapter.getLogger('gui', className='ImageViewer')
        self.logger.debug('Initializing ImageViewer.')
        
        super(QtWidgets.QWidget, self).__init__(parent)
        
        self.tab_layout = QtWidgets.QVBoxLayout(self)
        
        # Initialize tab screen
        self.tab_widget = QtWidgets.QTabWidget()
  
        # Add tabs to widget
        self.tab_layout.addWidget(self.tab_widget)
        self.setLayout(self.tab_layout)
        
        # Filter for properties (getters and setters) in Canvas class
        self.canvas_attrs = [attr for attr in dir(Canvas) if isinstance(getattr(Canvas, attr, None), property)]
        
        self.tabs = []
        
    @property
    def current_tab(self) -> int:
        return self.tab_widget.currentIndex()
    
    @current_tab.setter
    def current_tab(self, val: int) -> None:
        self.tab_widget.setCurrentIndex(val)
        
    def set_images(self, image_bytes_list: list[bytes], is_drawing_enabled: bool) -> None:
        
        self.logger.debug(f'Zipping image_bytes_list (len={len(image_bytes_list)}) and self.tabs (len={len(self.tabs)})')
        zipped = [
            (
                image_bytes_list[i] if i < len(image_bytes_list) else None,
                self.tabs[i] if i < len(self.tabs) else None
            )
            for i
            in range(max(len(image_bytes_list), len(self.tabs)))
        ]
        __zipped = [("..." if b is not None else None, t) for b, t in zipped]
        
        self.logger.debug(f'Iterating over: {__zipped}')
        
        for i, (img_bytes, tab) in enumerate(zipped):
            if tab is None:
                # tab doesn't exist for given img bytes -> create new tab
                self.logger.debug(f'{i}: {__zipped[i]} -> Create new tab.')
                
                # add tab to the widget and the list
                self.tabs.append(Canvas(img_bytes, is_drawing_enabled))
                self.tab_widget.addTab(self.tabs[i], str(i))
                
                # relay signals
                self.tabs[i].newTable.connect(lambda table: self.newTable.emit(table))
                self.tabs[i].tableUpdated.connect(lambda table_index, table: self.tableUpdated.emit(table_index, table))
                self.tabs[i].tableDeleted.connect(lambda table_index: self.tableDeleted.emit(table_index))
                self.tabs[i].tableSelected.connect(lambda table_index: self.tableSelected.emit(table_index))
                self.tabs[i].tableDeselected.connect(lambda: self.tableDeselected.emit())
                
            elif img_bytes is None:
                # tab exists already but the image bytes is not given -> remove tab
                self.logger.debug(f'{i}: {__zipped[i]} -> Remove tab.')
                
                self.tab_widget.removeTab(i)
                self.tabs.pop(i)
                
            else:
                # tab exists and the image_bytes has been given, update the image in the tab
                self.logger.debug(f'{i}: {__zipped[i]} -> Update tab image.')
                
                self.tabs[i].image_bytes = img_bytes
                
                
    def update_image(self, tab_index: int, image_bytes: bytes) -> None:
        print(f'ImageViewer.update_image: tab_index={tab_index}, image_bytes=...')
        self.tabs[tab_index].image_bytes = image_bytes
            
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

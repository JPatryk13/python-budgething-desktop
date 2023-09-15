from PyQt6 import QtWidgets, QtCore, QtGui

from budgeting_app.gui.services.table_extractor.image_tools import (
    Tools,
    AddMode,
    TableObjF,
    SelectedTable,
    ImageData,
    TableDrawingTool,
    DEFAULT_TOOL,
    DEFAULT_ADD_COLUMN_MODE,
    DEFAULT_ADD_ROW_MODE,
)
from budgeting_app.utils.tools import is_all_not_none


class ImageViewer(QtWidgets.QWidget):
    selected_tool: Tools
    images_data: list[ImageData]
    offset_x: float
    offset_y: float
    most_recent_scale_ratio: float
    col_count: int
    row_count: int
    add_column_mode: AddMode
    add_row_mode: AddMode
    start_pos: QtCore.QPointF | None
    end_pos: QtCore.QPointF | None
    tables: list[TableObjF]
    selected_table: SelectedTable | None
    selected_page_image_index: int

    newTable = QtCore.pyqtSignal(int, TableObjF)
    """
    Args:\n
        `page_index (int)` - index of the page where the table is created\n
        `table (TableObjF)` - new table object\n
    """
    
    tableUpdated = QtCore.pyqtSignal(int, int, TableObjF)
    """
    Args:\n
        `page_index (int)` - index of the page where the table is updated\n
        `table_index (int)` - index of the updated table\n
        `table (TableObjF)` - updated table object\n
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
        super().__init__(parent)
        self.selected_tool = DEFAULT_TOOL
        self.images_data = []
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.col_count = 2
        self.add_column_mode = DEFAULT_ADD_COLUMN_MODE
        self.row_count = 3
        self.add_row_mode = DEFAULT_ADD_ROW_MODE
        self.start_pos = None
        self.end_pos = None
        self.tables = []
        self.selected_table = None
        self.most_recent_scale_ratio = 1.0
        self.selected_page_image_index = 0

    def set_image(self, img_bytes_list: list[bytes]):
        img_list = [QtGui.QImage().fromData(QtCore.QByteArray(img_bytes)) for img_bytes in img_bytes_list]
        self.images_data = [ImageData(
            original_image=img,
            current_scaled_image=img,
            current_origin_pos=QtCore.QPointF(0.0, 0.0)
        ) for img in img_list]
        self.update_image_origin_pos()
        self.update()
        
    def change_current_page_image_index(self, image_index: int) -> None:
        self.selected_page_image_index = image_index

    def set_tool(self, tool: Tools) -> None:
        self.selected_tool = tool
        if tool != Tools.HAND_TOOL:
            # clear out the vars - they only make sense when using hand tool
            self.selected_table = None
        self.update()

    def set_add_column_mode(self, add_column_mode: AddMode) -> None:
        self.add_column_mode = add_column_mode

    def set_add_row_mode(self, add_row_mode: AddMode) -> None:
        self.add_row_mode = add_row_mode

    def set_col_count(self, col_count: int) -> None:
        if self.selected_table is not None:
            # Update number of column in existing table
            self.tables[self.selected_table.table_index] = TableDrawingTool.update_column_count(
                self.tables[self.selected_table.table_index],
                col_count,
                self.add_column_mode
            )
            self.update()
        else:
            # update column count in the tool settings
            self.col_count = col_count

    def set_row_count(self, row_count: int) -> None:
        if self.selected_table is not None:
            self.tables[self.selected_table.table_index] = TableDrawingTool.update_row_count(
                self.tables[self.selected_table.table_index],
                row_count,
                self.add_row_mode
            )
            self.update()
        else:
            self.row_count = row_count
            
    def update_image_origin_pos(self) -> tuple[float, float]:
        """
        Returns:
            tuple[float, float]: Image origin displacement `(dx, dy)`
        """
        # New postion of the image origin
        x = (self.width() - self.images_data[self.selected_page_image_index].current_scaled_image.width()) / 2 + self.offset_x
        y = (self.height() - self.images_data[self.selected_page_image_index].current_scaled_image.height()) / 2 + self.offset_y
        
        # Image origin displacement
        dx = x - self.images_data[self.selected_page_image_index].current_origin_pos.x()
        dy = y - self.images_data[self.selected_page_image_index].current_origin_pos.y()
        
        self.images_data[self.selected_page_image_index].current_origin_pos = QtCore.QPointF(x, y)
        
        return dx, dy

    def wheelEvent(self, event: QtGui.QWheelEvent):
        # Update image_data.current_size from event
        current_image_size = self.images_data.current_scaled_image.size()
        if event.angleDelta().y() > 0:
            current_image_size *= 1.1
        else:
            current_image_size /= 1.1
        
        # Update image from the 
        self.images_data[self.selected_page_image_index].current_scaled_image = self.images_data[self.selected_page_image_index].original_image.scaled(current_image_size, QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.update_image_origin_pos()
        self.tables, self.most_recent_scale_ratio = TableDrawingTool.update_tables_scale(self.tables, self.images_data[self.selected_page_image_index], self.most_recent_scale_ratio)
            
        self.update()
        
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        dx, dy = self.update_image_origin_pos()
        self.tables = TableDrawingTool.move_tables(self.tables, dx, dy)
        self.tables, self.most_recent_scale_ratio = TableDrawingTool.update_tables_scale(self.tables, self.images_data[self.selected_page_image_index], self.most_recent_scale_ratio)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.start_pos = event.position()
            self.end_pos = event.position()
            
            print(event.position())

            if self.selected_tool == Tools.HAND_TOOL and self.selected_table is not None:
                # That only runs when the selected tool is HAND_TOOL and we already have a table that is selected.
                # I want to 'register' the element on press so that it can be updated when the mouse button is pressed
                # and the coursor is being moved.
                self.selected_table = TableDrawingTool.get_table_element_by_handle(event.position(), self.selected_table)
        
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:

            if self.selected_tool == Tools.HAND_TOOL:

                if self.selected_table is None:

                    dx = event.position().x() - self.end_pos.x()
                    dy = event.position().y() - self.end_pos.y()
                    self.offset_x += dx
                    self.offset_y += dy
                    self.tables = TableDrawingTool.move_tables(self.tables, dx, dy)
                    self.images_data[self.selected_page_image_index].current_origin_pos += QtCore.QPointF(dx, dy)

                elif self.selected_table.selected_element is not None:
                    # if we selected a table and the mouse was clicked over one on the table element's handles,
                    # we want to move that element accordingly
                    self.tables[self.selected_table.table_index] = TableDrawingTool.update_table_element(
                        event.position(),
                        self.selected_table,
                    )

            self.end_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:

            if self.selected_tool == Tools.TABLE_DRAWING_TOOL \
                and is_all_not_none(self.start_pos, self.col_count, self.row_count):
                    # If the button was released when using TABLE_DRAWING_TOOL add a new table to the list
                    new_table = TableDrawingTool.get_table(
                        self.start_pos,
                        event.position(),
                        self.col_count,
                        self.row_count
                    )
                    self.tables.append(new_table)
                    self.newTable.emit(new_table)
                    
            elif self.selected_tool == Tools.HAND_TOOL:
                # If the button was released when using HAND_TOOL the behavior is different when we're holding
                # an element of the table or not
                if self.selected_table is None:
                    # when we're not holding any element verify if we're clocking on the table or not
                    table_index = TableDrawingTool.get_table_by_line(event.position(), self.tables)
                    if table_index is not None:
                        self.selected_table = SelectedTable(
                            table_index=table_index,
                            table_obj=self.tables[table_index],
                            selected_element=None
                        )
                        self.col_count = len(self.tables[table_index].vertical_separators) + 1
                        self.row_count = len(self.tables[table_index].horizontal_separators) + 1
                        self.tableSelected.emit(table_index)
                    else:
                        self.tableDeselected.emit()
                else:
                    # when we were holding an element just set selected_table_element to None
                    self.selected_table.selected_element = None

            self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        if self.images_data is not []:
            
            painter = QtGui.QPainter(self)
            painter.drawImage(self.images_data[self.selected_page_image_index].current_origin_pos, self.images_data[self.selected_page_image_index].current_scaled_image)

            if self.selected_tool == Tools.HAND_TOOL and self.selected_table is not None:
                TableDrawingTool.draw_selection_handles(painter, self.tables[self.selected_table.table_index])
            elif self.selected_tool == Tools.TABLE_DRAWING_TOOL and is_all_not_none(self.start_pos, self.end_pos, self.col_count, self.row_count):
                TableDrawingTool.draw(
                    painter=painter,
                    start_qpoint=self.start_pos,
                    end_qpoint=self.end_pos,
                    col_count=self.col_count,
                    row_count=self.row_count
                )
                

            TableDrawingTool.draw_all(painter, self.tables)

from dataclasses import dataclass
from enum import Enum
import math
from typing import Literal, TypedDict

from PyQt6 import QtGui, QtCore

from budgeting_app.utils.tools import (
    euclidean_distance,
    distance_from_line,
    is_all_not_none
)

DEFAULT_PEN = QtGui.QPen(QtGui.QColor(QtCore.Qt.GlobalColor.red))
DEFAULT_HANDLES_PEN = QtGui.QPen(QtGui.QColor(QtCore.Qt.GlobalColor.cyan))
SELECTION_HANDLE_RADIUS = 5
MIN_COLUMN_WIDTH = 4 * SELECTION_HANDLE_RADIUS
MIN_ROW_HEIGHT = 4 * SELECTION_HANDLE_RADIUS

class Tools(Enum):
    TABLE_DRAWING_TOOL = 0
    HAND_TOOL = 1

DEFAULT_TOOL = Tools.HAND_TOOL

class AddMode(Enum):
    INSERT_AT_END = 0
    APPEND = 1

DEFAULT_ADD_COLUMN_MODE = AddMode.INSERT_AT_END
DEFAULT_ADD_ROW_MODE = AddMode.APPEND
DEFAULT_ZOOM_FACTOR = 1.1

class TableObjData(TypedDict):
    top_left: tuple[float, float]
    bottom_right: tuple[float, float]
    vlines: list[float]
    hlines: list[float]

@dataclass
class TableObjF:
    """
        - boundary: `QtCore.QRectF` - rectangle surrounding the table
        - vertical_separators: `list[QtCore.QLineF]` - lines separating columns
        - horizontal_separators: `list[QtCore.QLineF]` - lines separating rows
    """
    boundary: QtCore.QRectF
    vertical_separators: list[QtCore.QLineF]
    horizontal_separators: list[QtCore.QLineF]
    
    def get_data(self) -> TableObjData:
        return TableObjData(
            top_left=(self.boundary.topLeft().x(), self.boundary.topLeft().y()),
            bottom_right=(self.boundary.bottomRight().x(), self.boundary.bottomRight().y()),
            vlines=[vl.x1() for vl in self.vertical_separators],
            hlines=[hl.y1() for hl in self.horizontal_separators],
        )
    
@dataclass
class SelectedElement:
    """
        - key: `str` - string representing property of the `TableObjF` object
        - index_or_loaction: `str | int` - if the `'boundary'` is selected as `key`, it is required
        to specify which corner of the boundary is selected, otherwise (if either vertical or
        horizontal line is selected) the index of the line must be given
    """
    key: Literal['boundary', 'vertical_separators', 'horizontal_separators']
    index_or_loaction: Literal['topLeft', 'topRight', 'bottomLeft', 'bottomRight'] | int
    
@dataclass
class SelectedTable:
    """
        - table_index: `int` - index of the selected table
        - table_obj: `TableObjF` - table at the given index
        - selected_element: `SelectedElement | None` - element of the table that has been selected (if any)
    """
    table_index: int
    table_obj: TableObjF
    selected_element: SelectedElement | None

@dataclass 
class ImageData:
    """
        - original_image: `QtGui.QImage` - image with the original dimensions
        - current_scaled_image: `QtGui.QImage` - image whose dimensions and position is adapted according to
        the user actions; i.e. zoom in = larger size, zoom out = smaller size, move 'camera' view = different
        image origin position
        - current_origin_pos: `QtCore.QPointF` - position of the top-left corner of the image with respect to
        the 'camera' view
    """
    original_image: QtGui.QImage
    current_scaled_image: QtGui.QImage
    current_origin_pos: QtCore.QPointF

class TableDrawingTool:

    @ classmethod
    def _min_table_width(cls, table: TableObjF) -> float:
        """Get minimum allowed width of the table
        """
        return (len(table.vertical_separators) + 1) * MIN_COLUMN_WIDTH
    
    @classmethod
    def _min_table_height(cls, table: TableObjF) -> float:
        """Get minimum allowed height of the table
        """
        return (len(table.horizontal_separators) + 1) * MIN_ROW_HEIGHT

    @classmethod
    def _get_lines(cls, boundary: QtCore.QRectF, div_count: int, axis: Literal['x', 'y'], dist_from_axis_distr: list[float] | None = None) -> list[QtCore.QLineF]:
        """Based on the table width/height, number `count` of columns/rows and distribution of lines calculate
        position and length of each line. If the distribution is not specified, calculate default value. I.e. equal
        width/height of each column/row.

        Args:
            boundary (QtCore.QRectF): Rectangle bounding the table
            count (int): Desired number of colums or rows
            axis (Literal[&#39;x&#39;, &#39;y&#39;]): generate vertical column separators if 'x' given, else generate
            horizontal row separators
            dist_from_axis_distr (list[float] | None, optional): Distribution of the distances between the left/top
            side of the table and the vertical/horizontal line given in terms of fractions of the width/height of
            the table.

        Raises:
            ValueError: Raised when the number of elements in the `dist_from_axis_distr` doesn't describe the number,
            `count` of columns/rows.

        Returns:
            list[QtCore.QLineF]: list of vertical/horizontal lines separating columns/rows.
        """
        if dist_from_axis_distr is not None:
            if len(dist_from_axis_distr) + 1 != div_count:
                raise ValueError
            else:
                distr = dist_from_axis_distr
        else:
            # E.g. count=5 => distr=[0.2, 0.4, 0.6, 0.8]
            distr = [(i + 1) / div_count for i in range(div_count - 1)]
            
        lines: list[QtCore.QLineF] = []
        # table lhs or top side (the side that is paraller and closest to the axis)
        tbl_origin_side_pos = getattr(boundary, 'left' if axis == 'x' else 'top')()
        # sides of the table that are bounding the line: (top, bottom) or (left, right)
        line_boundary1 = getattr(boundary, 'top' if axis == 'x' else 'left')()
        line_boundary2 = getattr(boundary, 'bottom' if axis == 'x' else 'right')()
        # table width/height
        tbl_side_length = getattr(boundary, 'width' if axis == 'x' else 'height')()
        
        # Find (x, y) values for each point. One coordinate will be constant across both points while the other
        # will be equal to the position of the sides of the border that are perpendicular to the line; i.e. if
        # the line is vertical both points will have the same x and the y will be equal to the position of the
        # top/bottom side of the border 
        for i in range(div_count - 1):
            # postion of the line along x/y axis
            pos = tbl_origin_side_pos + tbl_side_length * distr[i]
            
            # 'x': (pos, boundary.top()), (pos, boundary.bottom())
            # 'y': (boundary.left(), pos), (boundary.right(), pos)
            qpoint1 = QtCore.QPointF(
                pos if axis == 'x' else line_boundary1,
                line_boundary1 if axis == 'x' else pos
            )
            qpoint2 = QtCore.QPointF(
                pos if axis == 'x' else line_boundary2,
                line_boundary2 if axis == 'x' else pos
            )
            
            lines.append(QtCore.QLineF(qpoint1, qpoint2))

        return lines

    @classmethod    
    def _get_vlines(cls, boundary: QtCore.QRectF, col_count: int, distribution: list[float] | None = None) -> list[QtCore.QLineF]:
        """Based on the table width, desired count of columns and distribution of vertical lines calculate
        position and length of each line. If the distribution is not specified, calculate default value. I.e. equal
        width of each column.

        Args:
            boundary (QtCore.QRectF): Rectangle bounding the table
            col_count (int): Desired number of colums
            distribution (list[float] | None, optional): Distribution of the distances between the left side of the
            table and the vertical line given in terms of fractions of the width of the table.

        Returns:
            list[QtCore.QLineF]: list of vertical lines separating columns.
        """
        return cls._get_lines(boundary, col_count, 'x', distribution)
    
    @classmethod    
    def _get_hlines(cls, boundary: QtCore.QRectF, row_count: int, distribution: list[float] | None = None) -> list[QtCore.QLineF]:
        """Based on the table height, desired number of rows and distribution of lines calculate position and
        length of each line. If the distribution is not specified, calculate default value. I.e. equal height
        of each row.

        Args:
            boundary (QtCore.QRectF): Rectangle bounding the table
            row_count (int): Desired number of rows
            distribution (list[float] | None, optional): Distribution of the distances between the top side
            of the table and the horizontal line given in terms of fractions of the height of the table.

        Returns:
            list[QtCore.QLineF]: list of horizontal lines separating rows.
        """
        return cls._get_lines(boundary, row_count, 'y', distribution)
    
    @classmethod
    def _get_lines_distribution(cls, table: TableObjF, axis: Literal['x', 'y']) -> list[float]:
        """Calculate distribution of the distance of each vertical/horizontal line from the side
        of the boundary closest to the parallel axis and represent it as a fraction of the length
        of the perpendicular side of the boundary.
        
        Example:
            The table consist of boundary (width=200, height=300, top-left corner at x0=150, y0=100),
            two horizontal lines (y1=200, y2=350) and one vertical line (x1=200). The distribution for
            each dimension and each line will be calculated as follows:
            
                distr_x1 = |x1 - x0| / width = 0.25
                distr_y1 = |y1 - y0| / height = 0.(3)
                distr_y2 = |y2 - y0| / height = 0.8(3)
                
                distr_x = [0.25]
                distr_y = [0.(3), 0.8(3)]

        Args:
            table (TableObjF): table the lines will be pulled from
            axis (Literal[&#39;x&#39;, &#39;y&#39;]): axis that shall be considered - 'x' for distr_x
            and 'y' for distr_y

        Returns:
            list[float]: list of numbers where each one represents vertical/horizontal separator
            line distance from the left/top side of the boundary as a percent fraction of the total
            width/height of the table. For example, let's say we have a table with four columns
            and each column is 1/4 of the table's width. The distribution would be then
            [0.25, 0.5, 0.75]. Now, let's move the first vertical separator to the right.
            Now the distribution can be something like [0.35, 0.5, 0.75].
        """
        # table lhs or top side (the side that is paraller and closest to the axis)
        tbl_origin_side_pos = getattr(table.boundary, 'left' if axis == 'x' else 'top')()
        # table width/height
        tbl_side_length = getattr(table.boundary, 'width' if axis == 'x' else 'height')()
        
        distr: list[float] = []
        
        for line in getattr(table, 'vertical_separators' if axis == 'x' else 'horizontal_separators'):
            # let's say we have a table with two columns and two rows. Table's LHS dx=200, width w=100,
            # RHS dy=100, height h=150. Vertical separator is in the middle at x=250, horizontal separator
            # is at y=175. The distribution value for these lines can be calculated as follows
            #   distr_x = |x - dx| / w
            #   distr_y = |y - dy| / h
            # UPDATE: Column/row width/height, |x - dx| or |y - dy|, must be greater or equal MIN_COLUMN_WIDT
            # /MIN_ROW_HEIGHT, else it shall be set to the value of the latter one. Such change must be
            # accompanied by setting minimum width/height of a column/row.
            distr.append(abs(tbl_origin_side_pos - getattr(line.p1(), axis)()) / tbl_side_length) 
            
        return distr
    
    @classmethod
    def _get_vlines_distribution(cls, table: TableObjF) -> list[float]:
        """Calculate distribution of the distances of each vertical line from the left side of
        the boundary and represent it as a fraction of the table width.

        Args:
            table (TableObjF): table the lines will be pulled from

        Returns:
            list[float]: list of numbers where each one represents vertical separator line
            distance from the left side of the boundary as a percent fraction of the total
            width of the table.
        """
        return cls._get_lines_distribution(table, 'x')
    
    @classmethod
    def _get_hlines_distribution(cls, table: TableObjF) -> list[float]:
        """Calculate distribution of the distance of each horizontal line from the top side
        of the boundary and represent it as a fraction of the table height.

        Args:
            table (TableObjF): table the lines will be pulled from

        Returns:
            list[float]: list of numbers where each one represents horizontal separator
            line distance from the top side of the boundary as a percent fraction of the total
            height of the table.
        """
        return cls._get_lines_distribution(table, 'y')
    
    @classmethod
    def _get_line_translation_boundaries(
        cls,
        table: TableObjF,
        line_index: int,
        axis: Literal['x', 'y'],
        *,
        min_col_width: float = MIN_COLUMN_WIDTH,
        min_row_height: float = MIN_ROW_HEIGHT
    ) -> tuple[float, float]:
        """Each line (vertical/horizontal) can be moved only to an extent. The ultimate limit should be
        the line (or side of the boundary) that is next to it. Additionally it makes sense to specify
        minimum dimension of the div (col/row). That function allows to find allowed min and max value
        (along the axis the line is able to move, e.g. vertical separator can only move along x-axis)
        for any given line within the table.

        Args:
            table (TableObjF): Table the line belongs to
            line_index (int): Index of the line that we want min/max to be calculated for
            axis (Literal[&#39;x&#39;, &#39;y&#39;]): Axis along which the line is able to move
            min_col_width (float, optional): Minimum width of a column. Defaults to MIN_COLUMN_WIDTH.
            min_row_height (float, optional): Minimum width of a row. Defaults to MIN_ROW_HEIGHT.

        Returns:
            tuple[float, float]: Pair of points along the specified axis. E.g. for vertical separator
            it would be x_min, x_max.
        """
        boundary = table.boundary
        lines: list[QtCore.QLineF] = getattr(table, 'vertical_separators' if axis == 'x' else 'horizontal_separators')
        # sides of the table that are parallel to the line: [hline: (top, bottom)] or [vline: (left, right)]
        lines_translation_boundary1 = getattr(boundary, 'left' if axis == 'x' else 'top')()
        lines_translation_boundary2 = getattr(boundary, 'right' if axis == 'x' else 'bottom')()
        min_size = min_col_width if axis == 'x' else min_row_height
        
        ###########
        #   MIN   #
        ###########
        
        if line_index == 0:
            pos1 = lines_translation_boundary1
        else:
            pos1 = getattr(lines[line_index - 1].p1(), axis)()
        
        ###########
        #   MAX   #
        ###########
        
        if line_index == len(lines) - 1:
            pos2 = lines_translation_boundary2
        else:
            pos2 = getattr(lines[line_index + 1].p1(), axis)()
            
        # using min and max ensures that the first value is actually min and the second is actually max
        return min(pos1, pos2) + min_size, max(pos1, pos2) - min_size
    
    @classmethod
    def _get_vline_translation_boundaries(cls, table: TableObjF, line_index: int, min_col_width: float = MIN_COLUMN_WIDTH) -> tuple[float, float]:
        """Find allowed min and max value (along the x-axis - vertical separator can only move along
        x-axis) for any given vertical separator within the table.

        Args:
            table (TableObjF): Table the line belongs to
            line_index (int): Index of the line that we want min/max to be calculated for
            min_col_width (float, optional): Minimum width of a column. Defaults to MIN_COLUMN_WIDTH.

        Returns:
            tuple[float, float]: Pair of points along the x-axis. I.e. x_min, x_max.
        """
        return cls._get_line_translation_boundaries(table, line_index, 'x', min_col_width=min_col_width)

    @classmethod
    def _get_hline_translation_boundaries(cls, table: TableObjF, line_index: int, min_row_height: float = MIN_ROW_HEIGHT) -> tuple[float, float]:
        """Find allowed min and max value (along the y-axis - horizontal separator can only move along
        y-axis) for any given horizontal separator within the table.

        Args:
            table (TableObjF): Table the line belongs to
            line_index (int): Index of the line that we want min/max to be calculated for
            min_row_height (float, optional): Minimum height of a row. Defaults to MIN_ROW_HEIGHT.

        Returns:
            tuple[float, float]: Pair of points along the y-axis. I.e. y_min, y_max.
        """
        return cls._get_line_translation_boundaries(table, line_index, 'y', min_row_height=min_row_height)

    @classmethod    
    def draw(
        cls,
        *,
        painter: QtGui.QPainter,
        start_qpoint: QtCore.QPointF | None = None,
        end_qpoint: QtCore.QPointF | None = None,
        col_count: int | None = None,
        row_count: int | None = None,
        table: TableObjF | None = None
    ) -> None:
        """Draw a table using givent painter object. If `start_qpoint`, `end_qpoint`, `col_count` and
        `row_count` are given draw a table whose boudary top-left and bottom-right corners are placed at
        `start_qpoint` and `end_qpoint` respectively(?). The new table has default column and row
        distribution. If any of the previous values is not specified `table` is required (otherwise
        `ValueError` is raised). Then, when the `table` is given it draws it's boundary and given
        vlines/hlines.

        Args:
            painter (QtGui.QPainter): If the given painter object has any pen specified it will be overriden
            by (cyrrently) DEFAULT_PEN
            start_qpoint (QtCore.QPointF | None, optional): top-left or bottom-right corner of the table
            - idk which one. Defaults to None.
            end_qpoint (QtCore.QPointF | None, optional): top-left or bottom-right corner of the table.
            Defaults to None.
            col_count (int | None, optional): number of columns. Defaults to None.
            row_count (int | None, optional): number of rows. Defaults to None.
            table (TableObjF | None, optional): if the `start_qpoint`, `end_qpoint`, `col_count` and
            `row_count` are None then this value is used. Defaults to None.

        Raises:
            ValueError: Raised if any of the `start_qpoint`, `end_qpoint`, `col_count` and `row_count`
            are not specified as well as the `table` is not
        """
        painter.setPen(DEFAULT_PEN)
        if is_all_not_none(start_qpoint, end_qpoint, col_count, row_count):
            boundary = QtCore.QRectF(start_qpoint, end_qpoint)
            painter.drawRect(boundary)
            painter.drawLines([
                *cls._get_hlines(boundary, row_count),
                *cls._get_vlines(boundary, col_count)
            ])
        elif table is not None:
            painter.drawRect(table.boundary)
            painter.drawLines([
                *table.horizontal_separators,
                *table.vertical_separators
            ])
        else:
            raise ValueError

    @classmethod    
    def draw_all(cls, painter: QtGui.QPainter, tables: list[TableObjF]) -> None:
        """Draw all tables given in the list.
        """
        painter.setPen(DEFAULT_PEN)
        for table in tables:
            painter.drawRect(table.boundary)
            painter.drawLines([
                *table.horizontal_separators,
                *table.vertical_separators
            ])

    @classmethod
    def get_table(cls, start_qpoint: QtCore.QPointF, end_qpoint: QtCore.QPointF, col_count: int, row_count: int) -> TableObjF:
        """Create a TableObjF object from given `start_qpoint` and `end_qpoint` and with giben
        number of columns and rows. Vertical and horizontal separators are evenly spaced.
        """
        boundary = QtCore.QRectF(start_qpoint, end_qpoint)

        return TableObjF(
            boundary=boundary,
            vertical_separators=cls._get_vlines(boundary, col_count),
            horizontal_separators=cls._get_hlines(boundary, row_count)
        )

    @classmethod    
    def draw_selection_handles(cls, painter: QtGui.QPainter, table: TableObjF) -> None:
        """Selection handle are those little circles displayed around each 'grabable' point on the table.
        Each corner of the boundary can be grabbed and moved, therefore, they will have their handles.
        Each vertical and horizontal line has its handle around the top or left-hand-side point
        respectively.

        Args:
            painter (QtGui.QPainter): painter object to be used
            table (TableObjF): table for which the handles will be drawn
        """
        painter.setPen(DEFAULT_HANDLES_PEN)

        for point in [
            table.boundary.topLeft(),
            table.boundary.topRight(),
            table.boundary.bottomLeft(),
            table.boundary.bottomRight()
        ]:
            painter.drawEllipse(point, SELECTION_HANDLE_RADIUS, SELECTION_HANDLE_RADIUS)
            
        for vline in table.vertical_separators:
            painter.drawEllipse(
                vline.p2() if vline.p2().y() <= vline.p1().y() else vline.p1(),
                SELECTION_HANDLE_RADIUS,
                SELECTION_HANDLE_RADIUS
            )
            
        for hline in table.horizontal_separators:
            painter.drawEllipse(
                hline.p2() if hline.p2().x() >= hline.p1().x() else hline.p1(),
                SELECTION_HANDLE_RADIUS,
                SELECTION_HANDLE_RADIUS
            )
            
    @classmethod
    def move_tables(cls, tables: list[TableObjF], dx: float, dy: float) -> list[TableObjF]:
        """Move tables in the given list by dx distance in the x-direction and dy distance
        in the y-direction

        Args:
            tables (list[TableObjF]): List of tables to be affected
            dx (float): Distance in the x-direction
            dy (float): Distance in the y-direction

        Returns:
            list[TableObjF]: List of updated tables
        """
        for i, table in enumerate(tables):
            tables[i].boundary = QtCore.QRectF(
                table.boundary.topLeft() + QtCore.QPointF(dx, dy),
                table.boundary.bottomRight() + QtCore.QPointF(dx, dy)
            )
            for j, vline in enumerate(table.vertical_separators):
                tables[i].vertical_separators[j] = vline.translated(dx, dy)
            for j, hline in enumerate(table.horizontal_separators):
                tables[i].horizontal_separators[j] = hline.translated(dx, dy)

        return tables

    @classmethod    
    def get_table_element_by_handle(
        cls,
        pos: QtCore.QPointF,
        selected_table: SelectedTable
    ) -> SelectedTable:
        """Checks which element's handle the position of the coursor, `pos`, is closest to and
        within the selection handle. If any is found to match the criteria updates
        selected_table.selected_element approprietely and returns it.

        Args:
            pos (QtCore.QPointF): coursor position
            selected_table (SelectedTable): table that has been selected. Only such can be
            modified by dragging its components

        Returns:
            SelectedTable: Updated SelectedTable. If selected_element is None no element has
            been selected.
        """
        selected_table_with_element: SelectedTable = selected_table
        table = selected_table.table_obj
        min_distance: float = math.inf

        # Check boundary
        rect = table.boundary
        points = [rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()]
        for j, p in enumerate(points):
            dist = euclidean_distance(
                x1=p.x(),
                x2=pos.x(),
                y1=p.y(),
                y2=pos.y()
            )
            if dist <= SELECTION_HANDLE_RADIUS and dist < min_distance:
                selected_table_with_element.selected_element = SelectedElement(
                    key='boundary',
                    index_or_loaction=['topLeft', 'topRight', 'bottomLeft', 'bottomRight'][j]
                )
                min_distance = dist

        # Check vlines
        for j, vline in enumerate(table.vertical_separators):
            p = vline.p2() if vline.p2().y() <= vline.p1().y() else vline.p1()
            dist = euclidean_distance(
                x1=p.x(),
                x2=pos.x(),
                y1=p.y(),
                y2=pos.y()
            )
            if dist <= SELECTION_HANDLE_RADIUS and dist < min_distance:
                selected_table_with_element.selected_element = SelectedElement(
                    key='vertical_separators',
                    index_or_loaction=j
                )
                min_distance = dist

        # Check hlines
        for j, hline in enumerate(table.horizontal_separators):
            p = hline.p2() if hline.p2().x() >= hline.p1().x() else hline.p1()
            dist = euclidean_distance(
                x1=p.x(),
                x2=pos.x(),
                y1=p.y(),
                y2=pos.y()
            )
            if dist <= SELECTION_HANDLE_RADIUS and dist < min_distance:
                selected_table_with_element.selected_element = SelectedElement(
                    key='horizontal_separators',
                    index_or_loaction=j
                )
                min_distance = dist

        return selected_table

    @classmethod    
    def get_table_by_line(
        cls,
        pos: QtCore.QPointF,
        tables: list[TableObjF]
    ) -> int | None:
        """Find table (in the list) that the coursor is closest to (and closer that the
        SELECTION_HANDLE_RADIUS) one or more of its elements.

        Args:
            pos (QtCore.QPointF): position of the coursor
            tables (list[TableObjF]): list of tables to check

        Returns:
            int | None: Index of the table
        """
        min_distance: float = math.inf
        tbl_index: int | None = None

        for i, table in enumerate(tables):
            # Check boundary
            rect = table.boundary
            lines = [
                QtCore.QLineF(rect.topLeft(), rect.topRight()),
                QtCore.QLineF(rect.topRight(), rect.bottomRight()),
                QtCore.QLineF(rect.bottomRight(), rect.bottomLeft()),
                QtCore.QLineF(rect.bottomLeft(), rect.topLeft())
            ]
            for l in lines:
                dist = distance_from_line(
                    pos.x(),
                    pos.y(),
                    l.p1().x(),
                    l.p2().x(),
                    l.p1().y(),
                    l.p2().y()
                )
                if dist <= SELECTION_HANDLE_RADIUS and dist < min_distance:
                    tbl_index = i
                    min_distance = dist

            # Check vlines
            for vline in table.vertical_separators:
                dist = distance_from_line(
                    pos.x(),
                    pos.y(),
                    vline.p1().x(),
                    vline.p2().x(),
                    vline.p1().y(),
                    vline.p2().y()
                )
                if dist <= SELECTION_HANDLE_RADIUS and dist < min_distance:
                    tbl_index = i
                    min_distance = dist

            # Check hlines
            for hline in table.horizontal_separators:
                dist = distance_from_line(
                    pos.x(),
                    pos.y(),
                    hline.p1().x(),
                    hline.p2().x(),
                    hline.p1().y(),
                    hline.p2().y()
                )
                if dist <= SELECTION_HANDLE_RADIUS and dist < min_distance:
                    tbl_index = i
                    min_distance = dist
        
        return tbl_index
    
    @classmethod
    def update_table_size(
        cls,
        pos: QtCore.QPointF,
        table: TableObjF,
        handle_literal: Literal['topLeft', 'topRight', 'bottomLeft', 'bottomRight']
    ) -> TableObjF:
        """Update table size by moving one of its corners. Allows to select one handle (on one of the corners of
        the table's boundary) and move it to the point `pos`. Automatically, the opposite corner (along the
        diagonal e.g. topLeft is 'opposite' to bottomRight) remain in its original place while the other to adjust
        their postion to preserve rectangular shape of the boundary. The function also adjusts the position of each
        vline/hline based on their original distribution. 

        Args:
            pos (QtCore.QPointF): postion of the coursor
            table (TableObjF): table to be resized
            handle_literal (Literal[&#39;topLeft&#39;, &#39;topRight&#39;, &#39;bottomLeft&#39;,
            &#39;bottomRight&#39;]): handle that is being grabbed and dragged

        Returns:
            TableObjF: Updated table
        """
        # distance between handle and the coursor
        dx: float = pos.x() - getattr(table.boundary, handle_literal)().x()
        dy: float = pos.y() - getattr(table.boundary, handle_literal)().y()
        
        # new origin (top-left corner) position of the table - the conditions here make sure that it is only update
        # when neccesary. I.e. when the coursor is moving handle on the left side of the boundary ('topLeft',
        # 'bottomLeft') the x coordinate is being changed, if the coursor is moving handle on top ('topLeft',
        # 'topRight') the y coordinate is being changed
        x0 = pos.x() if 'left' in handle_literal.lower() else table.boundary.topLeft().x()
        y0 = pos.y() if 'top' in handle_literal else table.boundary.topLeft().y()

        # new width and height of the table
        width = table.boundary.width() + ( -dx if 'left' in handle_literal.lower() else dx)
        height = table.boundary.height() + (-dy if 'top' in handle_literal else dy)


        # new width and height of the table considering the minimum allowed dimensions
        width = max(width, cls._min_table_width(table))
        height = max(height, cls._min_table_height(table))

        # new boundary
        boundary = QtCore.QRectF(x0, y0, width, height)
        
        # recalculating vlines based on the original distribution
        vlines = cls._get_vlines(
            boundary=boundary,
            col_count=len(table.vertical_separators) + 1,
            distribution=cls._get_vlines_distribution(table)
        )

        # recalculating hlines based on the original distribution
        hlines = cls._get_hlines(
            boundary=boundary,
            row_count=len(table.horizontal_separators) + 1,
            distribution=cls._get_hlines_distribution(table)
        )

        return TableObjF(
            boundary=boundary,
            vertical_separators=vlines,
            horizontal_separators=hlines
        )
        
    @classmethod
    def update_tables_scale(cls, tables: list[TableObjF], image_data: ImageData, previous_ratio: float) -> tuple[list[TableObjF], float]:
        """Change the size of all tables in the list based on the change of the scale (size) of the image
        relative to it's original size.

        Args:
            tables (list[TableObjF]): Tables to be affected
            image_data (ImageData): Image data obj containing the original image (/w size), scaled image
            (/w size) and the (origin) position of the top-left corner of that image
            previous_ratio (float): Ratio of the scaled image size to the original image size that was
            used previously to recalculate size of tables

        Returns:
            tuple[list[TableObjF], float]: first item is the list with scaled tables and the second one is
            the new absolute ratio calculated
        """
        scaled_tables: list[TableObjF] = []
        
        # relative (to the previus one) ratio of the rescaled image's size to the original size
        ratio_x = image_data.current_scaled_image.size().width() / image_data.original_image.size().width()
        ratio_y = image_data.current_scaled_image.size().height() / image_data.original_image.size().height()
        abs_ratio = (ratio_x + ratio_y) / 2
        rel_ratio = abs_ratio / previous_ratio
        
        print(rel_ratio)
        
        # x and y coordinate of the centre of the image
        img_centre_x = image_data.current_origin_pos.x() + image_data.current_scaled_image.size().width() / 2
        img_centre_y = image_data.current_origin_pos.y() + image_data.current_scaled_image.size().height() / 2
        
        for table in tables:
            
            # preserve original vline and hline distr
            vline_distr = cls._get_vlines_distribution(table)
            hline_distr = cls._get_hlines_distribution(table)
            
            # lines connecting point in the middle of the image and the top-left/ bottom-right corners of the table
            line_top_left = QtCore.QLineF(QtCore.QPointF(img_centre_x, img_centre_y), table.boundary.topLeft())
            line_bottom_right = QtCore.QLineF(QtCore.QPointF(img_centre_x, img_centre_y), table.boundary.bottomRight())
            
            # resize the line based on the ratio
            scaled_line_top_left = line_top_left
            scaled_line_top_left.setLength(line_top_left.length() * rel_ratio)
            scaled_line_bottom_right = line_bottom_right
            scaled_line_bottom_right.setLength(line_bottom_right.length() * rel_ratio)
            
            # resize the table boundary beased on the 'p2' points that mark new topLeft and bottomRight corners
            scaled_boundary = QtCore.QRectF(scaled_line_top_left.p2(), scaled_line_bottom_right.p2())
            
            scaled_tables.append(
                TableObjF(
                    boundary=scaled_boundary,
                    vertical_separators=cls._get_vlines(scaled_boundary, len(vline_distr) + 1, vline_distr),
                    horizontal_separators=cls._get_hlines(scaled_boundary, len(hline_distr) + 1, hline_distr)
                )
            )
            
        return scaled_tables, abs_ratio

    @classmethod
    def update_table_element(
        cls,
        pos: QtCore.QPointF,
        selected_table: SelectedTable
    ) -> TableObjF:
        """Allows to change the position of the vertical and horizontal lines as well as the size of the
        table boundary while preserving distribution of the vlines and hlines.

        Args:
            pos (QtCore.QPointF): Current position of the coursor
            selected_table (SelectedTable): SelectedTable object containing details about the selected
            table as well as the element that is supposed to be translated/resized

        Raises:
            ValueError: Raised when `selected_element` is NoneType

        Returns:
            TableObjF: Updated Table object
        """
        if selected_table.selected_element is not None:
            # An element of the table has been selected ('grabbed')
            
            if selected_table.selected_element.key == 'boundary':
                # The handle is on the boundary
                return cls.update_table_size(pos, selected_table.table_obj, selected_table.selected_element.index_or_loaction)

            elif selected_table.selected_element.key == 'vertical_separators':
                # The handle is on one of the vertical lines
                
                # top and bottom y-coordinates of the line (x is constant across the line)
                y1 = selected_table.table_obj.boundary.top()
                y2 = selected_table.table_obj.boundary.bottom()
                
                # the distance that the line is allowed to travel in each direction along the x-axis
                xmin, xmax = cls._get_vline_translation_boundaries(selected_table.table_obj, selected_table.selected_element.index_or_loaction)
                
                # if the coursor is beyond either boundary the line will lock at it's min/max
                if pos.x() < xmin:
                    new_xpos = xmin
                elif pos.x() > xmax:
                    new_xpos = xmax
                else:
                    new_xpos = pos.x()

                # update the line with new coordinates
                selected_table.table_obj.vertical_separators[selected_table.selected_element.index_or_loaction] = QtCore.QLineF(QtCore.QPointF(new_xpos, y1), QtCore.QPointF(new_xpos, y2))
                
                return selected_table.table_obj
            
            elif selected_table.selected_element.key == 'horizontal_separators':
                # The handle is on one of the horizontal lines
                
                # left and right x-coordinates of the line (y is constant across the line)
                x1 = selected_table.table_obj.boundary.left()
                x2 = selected_table.table_obj.boundary.right()
                
                # the distance that the line is allowed to travel in each direction along the y-axis
                ymin, ymax = cls._get_hline_translation_boundaries(selected_table.table_obj, selected_table.selected_element.index_or_loaction)
                
                # if the coursor is beyond either boundary the line will lock at it's min/max
                if pos.y() < ymin:
                    new_ypos = ymin
                elif pos.y() > ymax:
                    new_ypos = ymax
                else:
                    new_ypos = pos.y()

                # update the line with new coordinates
                selected_table.table_obj.horizontal_separators[selected_table.selected_element.index_or_loaction] = QtCore.QLineF(QtCore.QPointF(x1, new_ypos), QtCore.QPointF(x2, new_ypos))
                
                return selected_table.table_obj
            
        else:
            raise ValueError('SelectedTable.SelectedElement cannot be NoneType to run this operation.')
        
    @classmethod
    def _update_division_count(cls, table: TableObjF, axis: Literal['x', 'y'], target_div_count: int, add_mode: AddMode) -> TableObjF:
        """Add vertical (`axis='x'`) or horizontal (`axis='y'`) div(s). If the add_mode is set to:
            - `AddMode.APPEND` the table will expand when adding column/row
            - `AddMode.INSERT_AT_END` the table size will remain the same and the width of existing
            columns (or height of existing rows) will be adjusted to squeeze in another div.
        The size of the newly added div is the same as the size of the most-right column (most-bottom
        row). The new width is calculated as follows:
        
        Example:
            Let's say we have a table with 3 columns and four rows:
            
            - boundary: x0=105, y0=35, width=100, height=150
            - vlines: x1=135, x2=155 [0.3, 0.5]
            - hlines: y1=95, y2=125, y3=155 [0.4, 0.6, 0.8]
                
            We want to add two columns and one row without changing the size of the table. We run the
            function with `axis='x'` telling it to add the new rows we require.
            ```
                # Evaluate distribution of distances of each vertical line from the LHS of the table
                # as a fraction of the width of the table
                lines_dist_from_axis_distr = [0.3, 0.5]
                # Translate that distribution into one where each fraction represents width of each column
                div_size_distr = [0.3, 0.2, 0.5]
                # Add new column
                div_size_distr = [0.3, 0.2, 0.5, 0.5]
                # normalise distribution of the widths/heights so that all the values add up to 1
                normalisation_const = 1 / (0.3 + 0.2 + 0.5 + 0.5) = 0.(6)
                new_div_size_distr  = [0.3*normalisation_const, 0.2*normalisation_const, 0.5*normalisation_const, 0.5*normalisation_const]
                                    = [0.2, 0.1(3), 0.(3), 0.(3)]
                # translate back to the lines_dist_from_axis_distr
                new_lines_dist_from_axis_distr = [0.2, 0.(3), 0.(6)]
            ```
            Then, that new distribution is applied to generate new vlines and optionally resize the table boundary and hlines.
            
        Args:
            table (TableObjF): table to add/subtract divs to/from
            axis (Literal[&#39;x&#39;, &#39;y&#39;]): 'x' -> add/subtract columns, 'y' -> add/subtract rows
            target_div_count (int): the desired number of columns/rows
            add_mode (AddMode): see beggining of the doc

        Raises:
            ValueError: raised when the target_div_count is smaller than one

        Returns:
            TableObjF: updated table
        """
        
        if target_div_count < 1:
            raise ValueError('target_div_count must be greater or equal 1')
        
        # i.e. dist of vlines from x-axis or hlines from y-axis (current table)
        lines_dist_from_axis_distr = cls._get_lines_distribution(table, axis)
        # i.e. width of columns or height of rows (current table)
        div_size_distr = [b - a for a, b in list(zip([0.0, *lines_dist_from_axis_distr], [*lines_dist_from_axis_distr, 1.0]))]
        # save the values that are being added to or removed from the div_size_distr for later.
        # They will be required if the add_mode is set to AddMode.APPEND
        boundary_size_change = 0.0
        
        for _ in range(abs(target_div_count - len(div_size_distr))):
            if target_div_count > len(div_size_distr):
                # Add division at the end
                div_size_distr.append(div_size_distr[-1])
                # save the added value
                boundary_size_change += div_size_distr[-1]

            else:
                # remove division from the end and save the removed distr value
                boundary_size_change -= div_size_distr.pop()
                
        # normalise distribution of the widths/heights so that all the values add up to 1
        normalisation_const = 1 / sum(div_size_distr)
        new_div_size_distr = [p * normalisation_const for p in div_size_distr]
        # translate distr of the div sizes to distr of their distances from corresponding axes
        new_lines_dist_from_axis_distr = [sum(new_div_size_distr[:i + 1]) for i in range(len(new_div_size_distr) - 1)]
        
        if add_mode == AddMode.APPEND:
            # update the boundary size
            width = table.boundary.width() * (1 + boundary_size_change) if axis == 'x' else table.boundary.width()
            height = table.boundary.height() if axis == 'x' else table.boundary.height() * (1 + boundary_size_change)
            boundary = QtCore.QRectF(table.boundary.x(), table.boundary.y(), width, height)
            
        else:
            # boundary remains as is
            boundary = table.boundary
        
        
        new_lines = cls._get_lines(boundary, target_div_count, axis, new_lines_dist_from_axis_distr)
        
        # Update length of the other separators. If the boundary hasn't been resized
        # (add_mode=AddMode.INSERT_AT_END) the new perpendicular lines will remain the
        # same length as they were before
        perpendicular_lines_distr = cls._get_lines_distribution(table, 'y' if axis == 'x' else 'x')
        perpendicular_lines = cls._get_lines(
            boundary,
            len(perpendicular_lines_distr) + 1,
            'y' if axis == 'x' else 'x',
            perpendicular_lines_distr
        )
            
        return TableObjF(
            boundary=boundary,
            vertical_separators=new_lines if axis == 'x' else perpendicular_lines,
            horizontal_separators=perpendicular_lines if axis == 'x' else new_lines
        )

    @classmethod
    def update_column_count(cls, table: TableObjF, col_count: int, add_column_mode: AddMode) -> TableObjF:
        """Add or remove a column. If the add_mode is set to:
            - `AddMode.APPEND` the table will expand when adding a column
            - `AddMode.INSERT_AT_END` the table width will remain the same and the width of existing
            columns will be adjusted to squeeze in another div.
        The width of the newly added column is the same as the width of the most-right column.
            
        Args:
            table (TableObjF): table to add/subtract columns to/from
            col_count (int): the desired number of columns
            add_mode (AddMode): see beggining of the doc

        Raises:
            ValueError: raised when the col_count is smaller than one

        Returns:
            TableObjF: updated table
        """
        return cls._update_division_count(table, 'x', col_count, add_column_mode)

    @classmethod
    def update_row_count(cls, table: TableObjF, row_count: int, add_row_mode: AddMode) -> TableObjF:
        """Add or remove a row. If the add_mode is set to:
            - `AddMode.APPEND` the table will expand when adding a row
            - `AddMode.INSERT_AT_END` the table height will remain the same and the height of existing
            rows will be adjusted to squeeze in another div.
        The height of the newly added row is the same as the height of the most-bottom row.
            
        Args:
            table (TableObjF): table to add/subtract rows to/from
            row_count (int): the desired number of rows
            add_mode (AddMode): see beggining of the doc

        Raises:
            ValueError: raised when the row_count is smaller than one

        Returns:
            TableObjF: updated table
        """
        return cls._update_division_count(table, 'y', row_count, add_row_mode)

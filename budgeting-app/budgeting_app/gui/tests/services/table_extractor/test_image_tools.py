import unittest
from dataclasses import asdict

from PyQt6 import QtCore

from budgeting_app.gui.services.table_extractor.image_tools import (
    DrawingSettings,
    TableInfo,
    AddMode,
    QTableF,
    SelectedElement,
    SelectedTable,
    TableDrawingTool,
    MIN_COLUMN_WIDTH,
    MIN_ROW_HEIGHT,
)
from budgeting_app.gui.utils.tools import PyQtAssert

class TestImageTools(unittest.TestCase):
    def setUp(self) -> None:
        self.boundary_0x0y100w150h = QtCore.QRectF(QtCore.QPointF(0.0, 0.0), QtCore.QPointF(100.0, 150.0))
        self.table_2c3r = QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
            ]
        )
        self.table_3c2r = QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(100/3, 0.0), QtCore.QPointF(100/3, 150.0)),
                QtCore.QLineF(QtCore.QPointF(200/3, 0.0), QtCore.QPointF(200/3, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
            ]
        )
        self.table_4c4r = QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 112.5), QtCore.QPointF(100.0, 112.5))
            ]
        )
        self.boundary_120x35y100w150h = QtCore.QRectF(QtCore.QPointF(120.0, 35.0), QtCore.QPointF(220.0, 185.0))
        self.table_2c3r120x35y = QTableF(
            boundary=self.boundary_120x35y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(120.0, 35.0), QtCore.QPointF(120.0, 185.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(120.0, 85.0), QtCore.QPointF(220.0, 85.0)),
                QtCore.QLineF(QtCore.QPointF(120.0, 135.0), QtCore.QPointF(220.0, 135.0))
            ]
        )
        self.boundary_105x35y100w150h = QtCore.QRectF(QtCore.QPointF(105.0, 35.0), QtCore.QPointF(205.0, 185.0))
        self.table_2c3r105x35y = QTableF(
            boundary=self.boundary_105x35y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(105.0, 35.0), QtCore.QPointF(105.0, 185.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(105.0, 85.0), QtCore.QPointF(205.0, 85.0)),
                QtCore.QLineF(QtCore.QPointF(105.0, 135.0), QtCore.QPointF(205.0, 135.0))
            ]
        )
        self.table_2c2r100x200y100w100h = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(100.0, 200.0), QtCore.QPointF(200.0, 300.0)),
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(150.0, 200.0), QtCore.QPointF(150.0, 300.0))],
            horizontal_separators=[QtCore.QLineF(QtCore.QPointF(100.0, 250.0), QtCore.QPointF(200.0, 250.0))]
        )
        self.table_2c2r250x350y100w100h = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(250.0, 350.0), QtCore.QPointF(350.0, 450.0)),
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(300.0, 350.0), QtCore.QPointF(300.0, 450.0))],
            horizontal_separators=[QtCore.QLineF(QtCore.QPointF(250.0, 400.0), QtCore.QPointF(350.0, 400.0))]
        )
        # that boundary surrounds the two tables above
        self.boundary_80x100y400w500h = QtCore.QRectF(QtCore.QPointF(80.0, 100.0), QtCore.QPointF(480.0, 600.0))

    #
    # min_table_width
    #
    
    def test__min_table_width_default_table(self) -> None:
        expected = 2 * MIN_COLUMN_WIDTH
        actual = TableDrawingTool._min_table_width(self.table_2c3r)
        self.assertEqual(expected, actual)
        
    def test__min_table_width_table_not_at_origin(self) -> None:
        expected = 2 * MIN_COLUMN_WIDTH
        actual = TableDrawingTool._min_table_width(self.table_2c3r105x35y)
        self.assertEqual(expected, actual)

    def test__min_table_width_mirrored_table(self) -> None:
        expected = 2 * MIN_COLUMN_WIDTH
        mirrored_table_2c3r = QTableF(
            boundary=self.table_2c3r.boundary.moveLeft(200.0),
            vertical_separators=[self.table_2c3r.vertical_separators[0].translated(100.0, 0.0)],
            horizontal_separators=[
                self.table_2c3r.horizontal_separators[0].translated(100.0, 0.0),
                self.table_2c3r.horizontal_separators[1].translated(100.0, 0.0)
            ]
        )
        actual = TableDrawingTool._min_table_width(mirrored_table_2c3r)
        self.assertEqual(expected, actual)

    #
    # min_table_height
    #

    def test__min_table_height_default_table(self) -> None:
        expected = 3 * MIN_ROW_HEIGHT
        actual = TableDrawingTool._min_table_height(self.table_2c3r)
        self.assertEqual(expected, actual)
        
    def test__min_table_height_table_not_at_origin(self) -> None:
        expected = 3 * MIN_ROW_HEIGHT
        actual = TableDrawingTool._min_table_height(self.table_2c3r105x35y)
        self.assertEqual(expected, actual)

    def test__min_table_height_mirrored_table(self) -> None:
        expected = 3 * MIN_ROW_HEIGHT
        mirrored_table_2c3r = QTableF(
            boundary=self.table_2c3r.boundary.moveTop(300.0),
            vertical_separators=[self.table_2c3r.vertical_separators[0].translated(0.0, 150.0)],
            horizontal_separators=[
                self.table_2c3r.horizontal_separators[0].translated(0.0, 150.0),
                self.table_2c3r.horizontal_separators[1].translated(0.0, 150.0)
            ]
        )
        actual = TableDrawingTool._min_table_height(mirrored_table_2c3r)
        self.assertEqual(expected, actual)
        
    #
    # get_lines
    #
    
    def test__get_lines_x_axis_no_distribution(self) -> None:
        expected = self.table_2c3r.vertical_separators
        actual = TableDrawingTool._get_lines(
            boundary=self.boundary_0x0y100w150h,
            div_count=2,
            axis='x'
        )
        self.assertEqual(len(expected), len(actual))
        PyQtAssert.equalLines(expected[0], actual[0])

    def test__get_lines_x_axis_with_distribution(self) -> None:
        expected = [QtCore.QLineF(QtCore.QPointF(20.0, 0.0), QtCore.QPointF(20.0, 150.0))]
        actual = TableDrawingTool._get_lines(
            boundary=self.boundary_0x0y100w150h,
            div_count=2,
            axis='x',
            dist_from_axis_distr=[0.2]
        )
        self.assertEqual(len(expected), len(actual))
        PyQtAssert.equalLines(expected[0], actual[0])
        
    def test__get_lines_x_axis_with_distribution_boundary_not_at_origin(self) -> None:
        expected = [QtCore.QLineF(QtCore.QPointF(125.0, 35.0), QtCore.QPointF(125.0, 185.0))]
        actual = TableDrawingTool._get_lines(
            boundary=self.boundary_105x35y100w150h,
            div_count=2,
            axis='x',
            dist_from_axis_distr=[0.2]
        )
        self.assertEqual(len(expected), len(actual))
        PyQtAssert.equalLines(expected[0], actual[0])
        
    def test__get_lines_y_axis_no_distribution(self) -> None:
        expected = self.table_2c3r.horizontal_separators
        actual = TableDrawingTool._get_lines(
            boundary=self.boundary_0x0y100w150h,
            div_count=3,
            axis='y'
        )
        self.assertEqual(expected, actual)

    def test__get_lines_y_axis_with_distribution(self) -> None:
        expected = [
            QtCore.QLineF(QtCore.QPointF(0.0, 40.0), QtCore.QPointF(100.0, 40.0)),
            QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
        ]
        actual = TableDrawingTool._get_lines(
            boundary=self.boundary_0x0y100w150h,
            div_count=3,
            axis='y',
            dist_from_axis_distr=[4/15, 2/3]
        )
        self.assertEqual(expected, actual)
        
    def test__get_lines_y_axis_with_distribution_boundary_not_at_origin(self) -> None:
        expected = [
            QtCore.QLineF(QtCore.QPointF(105.0, 75.0), QtCore.QPointF(205.0, 75.0)),
            QtCore.QLineF(QtCore.QPointF(105.0, 135.0), QtCore.QPointF(205.0, 135.0))
        ]
        actual = TableDrawingTool._get_lines(
            boundary=self.boundary_105x35y100w150h,
            div_count=3,
            axis='y',
            dist_from_axis_distr=[4/15, 2/3]
        )
        self.assertEqual(expected, actual)

    #
    # get_vlines
    #

    def test__get_vlines_no_distribution(self) -> None:
        expected = self.table_2c3r.vertical_separators
        actual = TableDrawingTool._get_vlines(
            boundary=self.boundary_0x0y100w150h,
            col_count=2
        )
        self.assertEqual(len(expected), len(actual))
        PyQtAssert.equalLines(expected[0], actual[0])

    def test__get_vlines_with_distribution(self) -> None:
        expected = [QtCore.QLineF(QtCore.QPointF(20.0, 0.0), QtCore.QPointF(20.0, 150.0))]
        actual = TableDrawingTool._get_vlines(
            boundary=self.boundary_0x0y100w150h,
            col_count=2,
            distribution=[0.2]
        )
        self.assertEqual(len(expected), len(actual))
        PyQtAssert.equalLines(expected[0], actual[0])
        
    #
    # get_lines_distribution
    #
    
    def test__get_lines_distribution_x_axis_default_table(self) -> None:
        expected = [0.5]
        actual = TableDrawingTool._get_lines_distribution(self.table_2c3r, 'x')
        self.assertEqual(expected, actual)

    def test__get_lines_distribution_x_axis_moved_vline(self) -> None:
        expected = [0.2]
        actual = TableDrawingTool._get_lines_distribution(QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(20.0, 0.0), QtCore.QPointF(20.0, 150.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
            ]
        ), 'x')
        self.assertEqual(expected, actual)
        
    def test__get_lines_distribution_x_axis_moved_vline_boundary_not_at_origin(self) -> None:
        expected = [0.2]
        actual = TableDrawingTool._get_lines_distribution(QTableF(
            boundary=self.boundary_105x35y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(20.0, 0.0), QtCore.QPointF(20.0, 150.0)).translated(105.0, 35.0)],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)).translated(105.0, 35.0),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0)).translated(105.0, 35.0)
            ]
        ), 'x')
        self.assertEqual(expected, actual)
        
    def test__get_lines_distribution_y_axis_default_table(self) -> None:
        expected = [1/3, 2/3]
        actual = TableDrawingTool._get_lines_distribution(self.table_2c3r, 'y')
        self.assertEqual(expected, actual)

    def test__get_lines_distribution_y_axis_moved_vline(self) -> None:
        expected = [4/15, 2/3]
        actual = TableDrawingTool._get_lines_distribution(QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 40.0), QtCore.QPointF(100.0, 40.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
            ]
        ), 'y')
        self.assertEqual(expected, actual)
        
    def test__get_lines_distribution_y_axis_moved_vline(self) -> None:
        expected = [4/15, 2/3]
        actual = TableDrawingTool._get_lines_distribution(QTableF(
            boundary=self.boundary_105x35y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)).translated(105.0, 35.0)],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 40.0), QtCore.QPointF(100.0, 40.0)).translated(105.0, 35.0),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0)).translated(105.0, 35.0)
            ]
        ), 'y')
        self.assertEqual(expected, actual)

    #
    # get_vlines_distribution
    #

    def test__get_vlines_distribution_default_table(self) -> None:
        expected = [0.5]
        actual = TableDrawingTool._get_vlines_distribution(self.table_2c3r)
        self.assertEqual(expected, actual)

    def test__get_vlines_distribution_moved_vline(self) -> None:
        expected = [0.2]
        actual = TableDrawingTool._get_vlines_distribution(QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(20.0, 0.0), QtCore.QPointF(20.0, 150.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
            ]
        ))
        self.assertEqual(expected, actual)

    #
    # get_hlines
    #

    def test__get_hlines_no_distribution(self) -> None:
        expected = self.table_2c3r.horizontal_separators
        actual = TableDrawingTool._get_hlines(
            boundary=self.boundary_0x0y100w150h,
            row_count=3
        )
        self.assertEqual(expected, actual)

    def test__get_hlines_with_distribution(self) -> None:
        expected = [
            QtCore.QLineF(QtCore.QPointF(0.0, 40.0), QtCore.QPointF(100.0, 40.0)),
            QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
        ]
        actual = TableDrawingTool._get_hlines(
            boundary=self.boundary_0x0y100w150h,
            row_count=3,
            distribution=[4/15, 2/3]
        )
        self.assertEqual(expected, actual)

    #
    # get_hlines_distribution
    #

    def test__get_hlines_distribution_default_table(self) -> None:
        expected = [1/3, 2/3]
        actual = TableDrawingTool._get_hlines_distribution(self.table_2c3r)
        self.assertEqual(expected, actual)

    def test__get_hlines_distribution_moved_vline(self) -> None:
        expected = [4/15, 2/3]
        actual = TableDrawingTool._get_hlines_distribution(QTableF(
            boundary=self.boundary_0x0y100w150h,
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 40.0), QtCore.QPointF(100.0, 40.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0))
            ]
        ))
        self.assertEqual(expected, actual)

    #
    # get_line_translation_boundaries
    #

    def test__get_line_translation_boundaries_x_axis_single_vline(self) -> None:
        expected = (MIN_COLUMN_WIDTH, self.table_2c3r.boundary.width() - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_2c3r, 0, 'x')
        self.assertEqual(expected, actual)
        
    def test__get_line_translation_boundaries_x_axis_single_vline_table_not_at_origin(self) -> None:
        expected = (105.0 + MIN_COLUMN_WIDTH, 105.0 + self.table_2c3r105x35y.boundary.width() - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_2c3r105x35y, 0, 'x')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_x_axis_two_vlines_check_left(self) -> None:
        expected = (MIN_COLUMN_WIDTH, 200/3 - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_3c2r, 0, 'x')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_x_axis_two_vlines_check_right(self) -> None:
        expected = (100/3 + MIN_COLUMN_WIDTH, 100 - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_3c2r, 1, 'x')
        self.assertEqual(expected, actual, self.table_3c2r)

    def test__get_line_translation_boundaries_x_axis_three_vlines_check_middle(self) -> None:
        expected = (25.0 + MIN_COLUMN_WIDTH, 75.0 - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_4c4r, 1, 'x')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_x_axis_non_default_min_col_width(self) -> None:
        expected = (26.0, 74.0)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_4c4r, 1, 'x', min_col_width=1)
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_y_axis_single_hline(self) -> None:
        expected = (MIN_ROW_HEIGHT, 150.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_3c2r, 0, 'y')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_y_axis_two_hlines_check_top(self) -> None:
        expected = (MIN_ROW_HEIGHT, 100.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_2c3r, 0, 'y')
        self.assertEqual(expected, actual)
        
    def test__get_line_translation_boundaries_y_axis_two_hlines_check_top_table_not_at_origin(self) -> None:
        expected = (35.0 + MIN_ROW_HEIGHT, 135.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_2c3r105x35y, 0, 'y')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_y_axis_two_hlines_check_bottom(self) -> None:
        expected = (50.0 + MIN_ROW_HEIGHT, 150.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_2c3r, 1, 'y')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_y_axis_three_hlines_check_middle(self) -> None:
        expected = (37.5 + MIN_ROW_HEIGHT, 112.5 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_4c4r, 1, 'y')
        self.assertEqual(expected, actual)

    def test__get_line_translation_boundaries_y_axis_non_default_min_row_height(self) -> None:
        expected = (1.0, 149.0)
        actual = TableDrawingTool._get_line_translation_boundaries(self.table_3c2r, 0, 'y', min_row_height=1)
        self.assertEqual(expected, actual)

    #
    # get_vline_translation_boundaries
    #

    def test__get_vline_translation_boundaries_single_vline(self) -> None:
        expected = (MIN_COLUMN_WIDTH, self.table_2c3r.boundary.width() - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_vline_translation_boundaries(self.table_2c3r, 0)
        self.assertEqual(expected, actual)

    def test__get_vline_translation_boundaries_two_vlines_check_left(self) -> None:
        expected = (MIN_COLUMN_WIDTH, 200/3 - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_vline_translation_boundaries(self.table_3c2r, 0)
        self.assertEqual(expected, actual)

    def test__get_vline_translation_boundaries_two_vlines_check_right(self) -> None:
        expected = (100/3 + MIN_COLUMN_WIDTH, 100 - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_vline_translation_boundaries(self.table_3c2r, 1)
        self.assertEqual(expected, actual, self.table_3c2r)

    def test__get_vline_translation_boundaries_three_vlines_check_middle(self) -> None:
        expected = (25.0 + MIN_COLUMN_WIDTH, 75.0 - MIN_COLUMN_WIDTH)
        actual = TableDrawingTool._get_vline_translation_boundaries(self.table_4c4r, 1)
        self.assertEqual(expected, actual)

    def test__get_vline_translation_boundaries_non_default_min_col_width(self) -> None:
        expected = (26.0, 74.0)
        actual = TableDrawingTool._get_vline_translation_boundaries(self.table_4c4r, 1, min_col_width=1)
        self.assertEqual(expected, actual)

    #
    # get_hline_translation_boundaries
    #

    def test__get_hline_translation_boundaries_single_hline(self) -> None:
        expected = (MIN_ROW_HEIGHT, 150.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_hline_translation_boundaries(self.table_3c2r, 0)
        self.assertEqual(expected, actual)

    def test__get_hline_translation_boundaries_two_hlines_check_top(self) -> None:
        expected = (MIN_ROW_HEIGHT, 100.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_hline_translation_boundaries(self.table_2c3r, 0)
        self.assertEqual(expected, actual)

    def test__get_hline_translation_boundaries_two_hlines_check_bottom(self) -> None:
        expected = (50.0 + MIN_ROW_HEIGHT, 150.0 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_hline_translation_boundaries(self.table_2c3r, 1)
        self.assertEqual(expected, actual)

    def test__get_hline_translation_boundaries_three_hlines_check_middle(self) -> None:
        expected = (37.5 + MIN_ROW_HEIGHT, 112.5 - MIN_ROW_HEIGHT)
        actual = TableDrawingTool._get_hline_translation_boundaries(self.table_4c4r, 1)
        self.assertEqual(expected, actual)

    def test__get_hline_translation_boundaries_non_default_min_row_height(self) -> None:
        expected = (1.0, 149.0)
        actual = TableDrawingTool._get_hline_translation_boundaries(self.table_3c2r, 0, min_row_height=1)
        self.assertEqual(expected, actual)

    #
    # draw
    #

    def test_draw_new_table(self) -> None:
        pass

    #
    # draw_all
    #

    def test_draw_all_empty_list(self) -> None:
        pass

    #
    # get_table
    #

    def test_get_table(self) -> None:
        actual = TableDrawingTool.get_table(
            start_qpoint=QtCore.QPointF(0, 0.0),
            end_qpoint=QtCore.QPointF(100.0,150.0),
            col_count=2,
            row_count=3
        )
        PyQtAssert.equalTables(asdict(self.table_2c3r), asdict(actual))

    #
    # draw_selection_handles
    #

    def test_draw_selection_handles(self) -> None:
        pass

    #
    # move_tables
    #

    def test_move_tables_empty_list(self) -> None:
        expected = []
        actual = TableDrawingTool.move_tables([], dx=5.0, dy=5.0)
        self.assertEqual(expected, actual)

    def test_move_tables_non_empty_list(self) -> None:
        expected = [
            QTableF(
                boundary=self.table_2c3r.boundary.translated(5.0, 5.0),
                vertical_separators=[self.table_2c3r.vertical_separators[0].translated(5.0, 5.0)],
                horizontal_separators=[
                    self.table_2c3r.horizontal_separators[0].translated(5.0, 5.0),
                    self.table_2c3r.horizontal_separators[1].translated(5.0, 5.0)
                ]
            )
        ]
        actual = TableDrawingTool.move_tables([self.table_2c3r], 5.0, 5.0)
        self.assertEqual(expected, actual)

    #
    # get_table_element_by_handle
    #

    def test_get_table_element_by_handle_no_elements_in_reach(self) -> None:
        selected_table = TableInfo(
            table_drawing_settings=DrawingSettings(
                col_count=len(self.table_2c3r.vertical_separators) + 1,
                row_count=len(self.table_2c3r.horizontal_separators) + 1
            ),
            selected_table=SelectedTable(index=0, table=self.table_2c3r),
        )
        
        expected = selected_table
        actual = TableDrawingTool.get_table_element_by_handle(QtCore.QPointF(150.0, 50.0), selected_table)
        
        self.assertEqual(expected, actual)

    def test_get_table_element_by_handle_one_element_in_reach_boundary(self) -> None:
        selected_table = TableInfo(
            table_drawing_settings=DrawingSettings(
                col_count=len(self.table_2c3r.vertical_separators) + 1,
                row_count=len(self.table_2c3r.horizontal_separators) + 1
            ),
            selected_table=SelectedTable(index=0, table=self.table_2c3r),
        )
        
        expected = selected_table
        expected.selected_element = SelectedElement(key='boundary', index_or_loaction='topRight')
        actual = TableDrawingTool.get_table_element_by_handle(QtCore.QPointF(100.0, 0.0), selected_table)
        
        self.assertEqual(expected, actual)

    def test_get_table_element_by_handle_one_element_in_reach_vline(self) -> None:
        selected_table = TableInfo(
            table_drawing_settings=DrawingSettings(
                col_count=len(self.table_2c3r.vertical_separators) + 1,
                row_count=len(self.table_2c3r.horizontal_separators) + 1
            ),
            selected_table=SelectedTable(index=0, table=self.table_2c3r),
        )
        
        expected = selected_table
        expected.selected_element = SelectedElement(key='vertical_separators', index_or_loaction=0)
        actual = TableDrawingTool.get_table_element_by_handle(QtCore.QPointF(50.0, 0.0), selected_table)
        
        self.assertEqual(expected, actual)

    def test_get_table_element_by_handle_one_element_in_reach_hline(self) -> None:
        selected_table = TableInfo(
            table_drawing_settings=DrawingSettings(
                col_count=len(self.table_2c3r.vertical_separators) + 1,
                row_count=len(self.table_2c3r.horizontal_separators) + 1
            ),
            selected_table=SelectedTable(index=0, table=self.table_2c3r),
        )
        
        expected = selected_table
        expected.selected_element = SelectedElement(key='horizontal_separators', index_or_loaction=0)
        actual = TableDrawingTool.get_table_element_by_handle(QtCore.QPointF(100.0, 50.0), selected_table)
        
        self.assertEqual(expected, actual)

    #
    # get_table_by_line
    #

    def test_get_table_by_line_empty_list(self) -> None:
        expected = None
        actual = TableDrawingTool.get_table_by_line(QtCore.QPointF(100.0, 50.0), [])
        self.assertEqual(expected, actual)

    def test_get_table_by_line_no_tables_in_reach(self) -> None:
        expected = None
        actual = TableDrawingTool.get_table_by_line(QtCore.QPointF(120.0, 25.0), [self.table_2c3r])
        self.assertEqual(expected, actual)

    def test_get_table_by_line_one_table_in_reach(self) -> None:
        expected = 0
        actual = TableDrawingTool.get_table_by_line(QtCore.QPointF(100.0, 25.0), [self.table_2c3r])
        self.assertEqual(expected, actual)

    def test_get_table_by_line_two_tables_in_reach(self) -> None:
        expected = 1
        actual = TableDrawingTool.get_table_by_line(QtCore.QPointF(103.0, 45.0), [self.table_2c3r, self.table_2c3r105x35y])
        self.assertEqual(expected, actual)

    #
    # update_table_size
    #

    def test_update_table_size_handle_literal_topLeft(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(0.0, 0.0), QtCore.QPointF(110.0, 160.0)),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(55.0, 0.0), QtCore.QPointF(55.0, 160.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 160/3), QtCore.QPointF(110.0, 160/3)),
                QtCore.QLineF(QtCore.QPointF(0.0, 320/3), QtCore.QPointF(110.0, 320/3))
            ]
        )
        actual = TableDrawingTool.update_table_size(QtCore.QPointF(110.0, 160.0), self.table_2c3r, 'bottomRight')
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_size_handle_literal_topRight(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(0.0, 10.0), QtCore.QPointF(90.0, 150.0)),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(45.0, 10.0), QtCore.QPointF(45.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 170/3), QtCore.QPointF(90.0, 170/3)),
                QtCore.QLineF(QtCore.QPointF(0.0, 310/3), QtCore.QPointF(90.0, 310/3))
            ]
        )
        actual = TableDrawingTool.update_table_size(QtCore.QPointF(90.0, 10.0), self.table_2c3r, 'topRight')
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_size_handle_literal_bottomLeft(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(10.0, 10.0), QtCore.QPointF(100.0, 150.0)),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(55.0, 10.0), QtCore.QPointF(55.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(10.0, 170/3), QtCore.QPointF(100.0, 170/3)),
                QtCore.QLineF(QtCore.QPointF(10.0, 310/3), QtCore.QPointF(100.0, 310/3))
            ]
        )
        actual = TableDrawingTool.update_table_size(QtCore.QPointF(10.0, 10.0), self.table_2c3r, 'topLeft')
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_size_handle_literal_bottomRight(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(10.0, 0.0), QtCore.QPointF(100.0, 160.0)),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(55.0, 0.0), QtCore.QPointF(55.0, 160.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(10.0, 160/3), QtCore.QPointF(100.0, 160/3)),
                QtCore.QLineF(QtCore.QPointF(10.0, 320/3), QtCore.QPointF(100.0, 320/3))
            ]
        )
        actual = TableDrawingTool.update_table_size(QtCore.QPointF(10.0, 160.0), self.table_2c3r, 'bottomLeft')
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    #
    # update_tables_scale
    #
    
    def test_update_tables_scale_single_table_zoom_in(self) -> None:
        # tested manually :/
        pass
    
    def test_update_tables_scale_two_tables_zoom_in(self) -> None:
        pass
    
    def test_update_tables_scale_single_table_zoom_out(self) -> None:
        pass
    
    def test_update_tables_scale_two_tables_zoom_out(self) -> None:
        pass

    #
    # update_table_element
    #

    def test_update_table_element_boundary_handle_literal_topLeft(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(QtCore.QPointF(10.0, 10.0), QtCore.QPointF(100.0, 150.0)),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(55.0, 10.0), QtCore.QPointF(55.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(10.0, 170/3), QtCore.QPointF(100.0, 170/3)),
                QtCore.QLineF(QtCore.QPointF(10.0, 310/3), QtCore.QPointF(100.0, 310/3))
            ]
        )
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(10.0, 10.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='boundary', index_or_loaction='topLeft')
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_vline_pos_within_the_range(self) -> None:
        expected = self.table_2c3r
        expected.vertical_separators = [QtCore.QLineF(QtCore.QPointF(55.0, 0.0), QtCore.QPointF(55.0, 150.0))]
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(55.0, 0.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='vertical_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_vline_pos_gt_xmax(self) -> None:
        expected = self.table_2c3r
        newx = expected.boundary.topRight().x() - MIN_COLUMN_WIDTH
        expected.vertical_separators = [QtCore.QLineF(QtCore.QPointF(newx, 0.0), QtCore.QPointF(newx, 150.0))]
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(100.0, 0.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='vertical_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_vline_pos_lt_xmin(self) -> None:
        expected = self.table_2c3r
        expected.vertical_separators = [QtCore.QLineF(QtCore.QPointF(MIN_COLUMN_WIDTH, 0.0), QtCore.QPointF(MIN_COLUMN_WIDTH, 150.0))]
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(0.0, 0.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='vertical_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_vline_pos_within_the_range_below_table(self) -> None:
        expected = self.table_2c3r
        expected.vertical_separators = [QtCore.QLineF(QtCore.QPointF(55.0, 0.0), QtCore.QPointF(55.0, 150.0))]
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(55.0, 160.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='vertical_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_hline_pos_within_the_range(self) -> None:
        expected = self.table_2c3r
        expected.horizontal_separators[0] = QtCore.QLineF(QtCore.QPointF(0.0, 55.0), QtCore.QPointF(100.0, 55.0))
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(0.0, 55.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='horizontal_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_hline_pos_gt_ymax(self) -> None:
        expected = self.table_2c3r
        newy = 100.0 - MIN_ROW_HEIGHT
        expected.horizontal_separators[0] = QtCore.QLineF(QtCore.QPointF(0.0, newy), QtCore.QPointF(100.0, newy))
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(0.0, 150.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='horizontal_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_table_element_hline_pos_lt_ymin(self) -> None:
        expected = self.table_2c3r
        expected.horizontal_separators[0] = QtCore.QLineF(QtCore.QPointF(0.0, MIN_ROW_HEIGHT), QtCore.QPointF(100.0, MIN_ROW_HEIGHT))
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(0.0, 0.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='horizontal_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))
    
    def test_update_table_element_hline_pos_within_the_range_outside_table(self) -> None:
        expected = self.table_2c3r
        expected.horizontal_separators[0] = QtCore.QLineF(QtCore.QPointF(0.0, 55.0), QtCore.QPointF(100.0, 55.0))
        actual = TableDrawingTool.update_table_element(
            QtCore.QPointF(120.0, 55.0),
            TableInfo(
                table_drawing_settings=DrawingSettings(
                    col_count=len(self.table_2c3r.vertical_separators) + 1,
                    row_count=len(self.table_2c3r.horizontal_separators) + 1
                ),
                selected_table=SelectedTable(index=0, table=self.table_2c3r),
                selected_element=SelectedElement(key='horizontal_separators', index_or_loaction=0)
            )
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))
        
    #
    # update_division_count
    #

    def test__update_division_count_x_axis_insert_at_end_add_one_column(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(100/3, 0.0), QtCore.QPointF(100/3, 150.0)),
                QtCore.QLineF(QtCore.QPointF(200/3, 0.0), QtCore.QPointF(200/3, 150.0))
            ],
            horizontal_separators=self.table_2c3r.horizontal_separators
        )
        actual = TableDrawingTool._update_division_count(self.table_2c3r, 'x', 3, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_insert_at_end_add_two_columns(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 150.0))
            ],
            horizontal_separators=self.table_2c3r.horizontal_separators
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 4, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_insert_at_end_remove_one_column(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=self.table_2c3r.boundary,
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(100/3, 0.0), QtCore.QPointF(100/3, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(200/3, 0.0), QtCore.QPointF(200/3, 150.0))
                ],
                horizontal_separators=self.table_2c3r.horizontal_separators
            ),
            2,
            AddMode.INSERT_AT_END
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_insert_at_end_remove_two_columns(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=self.table_2c3r.boundary,
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 150.0))
                ],
                horizontal_separators=self.table_2c3r.horizontal_separators
            ),
            2,
            AddMode.INSERT_AT_END
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_insert_at_end_do_nothing(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 2, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_append_add_one_column(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 150.0, 150.0),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(150.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(150.0, 100.0))
            ]
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 3, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_append_add_two_columns(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 200.0, 150.0),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(150.0, 0.0), QtCore.QPointF(150.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(200.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(200.0, 100.0))
            ]
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 4, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_append_remove_one_column(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=QtCore.QRectF(0.0, 0.0, 150.0, 150.0),
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0)),
                ],
                horizontal_separators=[
                    QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(150.0, 50.0)),
                    QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(150.0, 100.0))
                ]
            ),
            2,
            AddMode.APPEND
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_append_remove_two_columns(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=QtCore.QRectF(0.0, 0.0, 200.0, 150.0),
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(150.0, 0.0), QtCore.QPointF(150.0, 150.0))
                ],
                horizontal_separators=[
                    QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(200.0, 50.0)),
                    QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(200.0, 100.0))
                ]
            ),
            2,
            AddMode.APPEND
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_x_axis_append_do_nothing(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 2, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_insert_at_end_add_one_row(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=self.table_2c3r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 112.5), QtCore.QPointF(100.0, 112.5))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 4, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_insert_at_end_add_two_rows(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=self.table_2c3r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 30.0), QtCore.QPointF(100.0, 30.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 60.0), QtCore.QPointF(100.0, 60.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 90.0), QtCore.QPointF(100.0, 90.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 120.0), QtCore.QPointF(100.0, 120.0)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 5, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_insert_at_end_remove_one_row(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=self.table_2c3r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 2, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_insert_at_end_remove_two_rows(self) -> None:
        expected = QTableF(
            boundary=self.table_4c4r.boundary,
            vertical_separators=self.table_4c4r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 2, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_insert_at_end_do_nothing(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 3, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_append_add_one_row(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 200.0),
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 200.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 150.0), QtCore.QPointF(100.0, 150.0))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 4, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_append_add_two_rows(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 250.0),
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 250.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 150.0), QtCore.QPointF(100.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 200.0), QtCore.QPointF(100.0, 200.0))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 5, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_append_remove_one_row(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 112.5),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 112.5)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 112.5)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 112.5))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 3, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_append_remove_two_rows(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 75.0),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 75.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 2, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test__update_division_count_y_axis_append_do_nothing(self) -> None:
        expected = self.table_4c4r
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 4, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    #
    # update_column_count
    #

    def test_update_column_count_insert_at_end_add_one_column(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(100/3, 0.0), QtCore.QPointF(100/3, 150.0)),
                QtCore.QLineF(QtCore.QPointF(200/3, 0.0), QtCore.QPointF(200/3, 150.0))
            ],
            horizontal_separators=self.table_2c3r.horizontal_separators
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 3, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_insert_at_end_add_two_columns(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 150.0))
            ],
            horizontal_separators=self.table_2c3r.horizontal_separators
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 4, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_insert_at_end_remove_one_column(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=self.table_2c3r.boundary,
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(100/3, 0.0), QtCore.QPointF(100/3, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(200/3, 0.0), QtCore.QPointF(200/3, 150.0))
                ],
                horizontal_separators=self.table_2c3r.horizontal_separators
            ),
            2,
            AddMode.INSERT_AT_END
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_insert_at_end_remove_two_columns(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=self.table_2c3r.boundary,
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 150.0))
                ],
                horizontal_separators=self.table_2c3r.horizontal_separators
            ),
            2,
            AddMode.INSERT_AT_END
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_insert_at_end_do_nothing(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 2, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_append_add_one_column(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 150.0, 150.0),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(150.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(150.0, 100.0))
            ]
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 3, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_append_add_two_columns(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 200.0, 150.0),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(150.0, 0.0), QtCore.QPointF(150.0, 150.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(200.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(200.0, 100.0))
            ]
        )
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 4, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_append_remove_one_column(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=QtCore.QRectF(0.0, 0.0, 150.0, 150.0),
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0)),
                ],
                horizontal_separators=[
                    QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(150.0, 50.0)),
                    QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(150.0, 100.0))
                ]
            ),
            2,
            AddMode.APPEND
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_append_remove_two_columns(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(
            QTableF(
                boundary=QtCore.QRectF(0.0, 0.0, 200.0, 150.0),
                vertical_separators=[
                    QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(100.0, 0.0), QtCore.QPointF(100.0, 150.0)),
                    QtCore.QLineF(QtCore.QPointF(150.0, 0.0), QtCore.QPointF(150.0, 150.0))
                ],
                horizontal_separators=[
                    QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(200.0, 50.0)),
                    QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(200.0, 100.0))
                ]
            ),
            2,
            AddMode.APPEND
        )
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_column_count_append_do_nothing(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_column_count(self.table_2c3r, 2, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))
    
    #
    # update_row_count
    #

    def test_update_row_count_insert_at_end_add_one_row(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=self.table_2c3r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 112.5), QtCore.QPointF(100.0, 112.5))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 4, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_insert_at_end_add_two_rows(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=self.table_2c3r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 30.0), QtCore.QPointF(100.0, 30.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 60.0), QtCore.QPointF(100.0, 60.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 90.0), QtCore.QPointF(100.0, 90.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 120.0), QtCore.QPointF(100.0, 120.0)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 5, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_insert_at_end_remove_one_row(self) -> None:
        expected = QTableF(
            boundary=self.table_2c3r.boundary,
            vertical_separators=self.table_2c3r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 2, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_insert_at_end_remove_two_rows(self) -> None:
        expected = QTableF(
            boundary=self.table_4c4r.boundary,
            vertical_separators=self.table_4c4r.vertical_separators,
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 2, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_insert_at_end_do_nothing(self) -> None:
        expected = self.table_2c3r
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 3, AddMode.INSERT_AT_END)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_append_add_one_row(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 200.0),
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 200.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 150.0), QtCore.QPointF(100.0, 150.0))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 4, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_append_add_two_rows(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 250.0),
            vertical_separators=[QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 250.0))],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 50.0), QtCore.QPointF(100.0, 50.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 100.0), QtCore.QPointF(100.0, 100.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 150.0), QtCore.QPointF(100.0, 150.0)),
                QtCore.QLineF(QtCore.QPointF(0.0, 200.0), QtCore.QPointF(100.0, 200.0))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_2c3r, 5, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_append_remove_one_row(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 112.5),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 112.5)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 112.5)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 112.5))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
                QtCore.QLineF(QtCore.QPointF(0.0, 75.0), QtCore.QPointF(100.0, 75.0))
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 3, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_append_remove_two_rows(self) -> None:
        expected = QTableF(
            boundary=QtCore.QRectF(0.0, 0.0, 100.0, 75.0),
            vertical_separators=[
                QtCore.QLineF(QtCore.QPointF(25.0, 0.0), QtCore.QPointF(25.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(50.0, 0.0), QtCore.QPointF(50.0, 75.0)),
                QtCore.QLineF(QtCore.QPointF(75.0, 0.0), QtCore.QPointF(75.0, 75.0))
            ],
            horizontal_separators=[
                QtCore.QLineF(QtCore.QPointF(0.0, 37.5), QtCore.QPointF(100.0, 37.5)),
            ]
        )
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 2, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    def test_update_row_count_append_do_nothing(self) -> None:
        expected = self.table_4c4r
        actual = TableDrawingTool.update_row_count(self.table_4c4r, 4, AddMode.APPEND)
        PyQtAssert.equalTables(asdict(expected), asdict(actual))

    


if __name__ == '__main__':
    unittest.main()
import sys
import unittest
from pathlib import Path

from PyQt6 import QtTest, QtWidgets, QtCore, QtGui
from pdfplumber import open as pdf_open

from budgeting_app.gui.services.drag_n_drop.drag_n_drop import AddDataFromFile
from budgeting_app.gui.services.table_extractor.table_extractor import TableExtractor
from budgeting_app.pdf_table_reader.core.entities.models import PDFFileWrapper, PDFPageWrapper


app = QtWidgets.QApplication(sys.argv)

class TestOpenFile(unittest.TestCase):
    def setUp(self):
        # Initialize the PyQt application
        self.window = AddDataFromFile()
        self.window.show()
        self.window_center = [
            int(self.window.geometry().x() + self.window.geometry().width() / 2),
            int(self.window.geometry().y() + self.window.geometry().height() / 2)
        ]

    def tearDown(self):
        # Close the application and clean up
        self.window.close()
        
    def test_drag_enter_event_pdf_file(self) -> None:
        mime_data = QtCore.QMimeData()
        mime_data.setUrls([QtCore.QUrl.fromLocalFile('sample.pdf')])
        drag_enter_event = QtGui.QDragEnterEvent(
            QtCore.QPoint(*self.window_center),
            QtCore.Qt.DropAction.MoveAction,
            mime_data,
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        QtCore.QCoreApplication.sendEvent(self.window, drag_enter_event)
        self.assertTrue(drag_enter_event.isAccepted())
        
    def test_drag_enter_event_csv_file(self) -> None:
        mime_data = QtCore.QMimeData()
        mime_data.setUrls([QtCore.QUrl.fromLocalFile('sample.csv')])
        drag_enter_event = QtGui.QDragEnterEvent(
            QtCore.QPoint(*self.window_center),
            QtCore.Qt.DropAction.MoveAction,
            mime_data,
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        QtCore.QCoreApplication.sendEvent(self.window, drag_enter_event)
        self.assertTrue(drag_enter_event.isAccepted())
        
    def test_drag_enter_event_json_file(self) -> None:
        mime_data = QtCore.QMimeData()
        mime_data.setUrls([QtCore.QUrl.fromLocalFile('sample.json')])
        drag_enter_event = QtGui.QDragEnterEvent(
            QtCore.QPoint(*self.window_center),
            QtCore.Qt.DropAction.MoveAction,
            mime_data,
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        QtCore.QCoreApplication.sendEvent(self.window, drag_enter_event)
        self.assertTrue(drag_enter_event.isAccepted())
        
    def test_drag_enter_event_wrong_file_format(self) -> None:
        mime_data = QtCore.QMimeData()
        mime_data.setUrls([QtCore.QUrl.fromLocalFile('sample.docx')])
        drag_enter_event = QtGui.QDragEnterEvent(
            QtCore.QPoint(*self.window_center),
            QtCore.Qt.DropAction.MoveAction,
            mime_data,
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        QtCore.QCoreApplication.sendEvent(self.window, drag_enter_event)
        self.assertTrue(not drag_enter_event.isAccepted())
        
    def test_drop_event_pdf_file(self) -> None:
        file_path_str = str(Path(__file__).parent.parent / 'integration_tests/data/1_table_1_page.pdf')
        
        mime_data = QtCore.QMimeData()
        mime_data.setUrls([QtCore.QUrl.fromLocalFile(file_path_str)])
        drop_event = QtGui.QDropEvent(
            QtCore.QPointF(*self.window_center),
            QtCore.Qt.DropAction.CopyAction,
            mime_data,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifier.NoModifier,
            QtCore.QEvent.Type.Drop
        )
        QtCore.QCoreApplication.sendEvent(self.window, drop_event)
        
        # Check pdf_table_reader_table_detector TableExtractor object
        # pdf_file = pdf_open(file_path_str)
        # pdf_file_wrapper = PDFFileWrapper(
        #     pages=[
        #         PDFPageWrapper(
        #             page=pdf_file.pages[0],
        #             elements=[],
        #             table_settings={}
        #         )
        #     ]
        # )
        # self.assertTrue(self.window.pdf_table_reader_table_detector is not None)
        # self.assertEqual(self.window.pdf_table_reader_table_detector.pdf_file, pdf_file_wrapper)
        
        # Check if the table extractor window is open
        
        QtTest.QTest.qWaitForWindowExposed(self.window.table_extractor_from_pdf)
        # QtTest.QTest.qWaitForWindowActive(services['table_extractor_from_pdf'])
        self.assertTrue(self.window.table_extractor_from_pdf.is_active_table_extractor_from_pdf)
        self.assertTrue(services['table_extractor_from_pdf'].isActiveWindow())
        
        # pdf_file.close()

    def test_drop_event_csv_file(self) -> None:
        pass

    def test_drop_event_json_file(self) -> None:
        pass

    def test_drop_event_wrong_file_format(self) -> None:
        pass

        
if __name__ == "__main__":
    unittest.main()
        
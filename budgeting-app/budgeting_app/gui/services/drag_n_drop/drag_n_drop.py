import sys
from typing import Any
import logging

from PyQt6.QtWidgets import (
    QLabel,
    QApplication,
    QWidget,
    QVBoxLayout
)
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPaintEvent,
    QPen,
    QDragEnterEvent,
    QDropEvent
)
from PyQt6.QtCore import Qt, QPoint

from budgeting_app.gui.services.base import MainWindow, ServiceManager
from budgeting_app.pdf_table_reader.core.usecases.pdf_reader import PDFReader
from budgeting_app.utils.logging import CustomLoggerAdapter


DEFAULT_BORDER_COLOR = QColor('#c5c5ca')
DEFAULT_BORDER_STYLE = [2, 4, 2, 4]
DEFAULT_BORDER_RADIUS = 30
DEFAULT_BORDER_WIDTH = 8
DEFAULT_TEXT_COLOR = QColor('#c5c5ca')
DEFAULT_FONT_SIZE = 18
DEFAULT_FONT_WEIGHT = 'bold'
DEFAULT_FONT_FAMILY = 'Arial'
RECOGNISED_FILETYPES = ('.pdf', '.csv', '.json')


class DragNDropLabel(QWidget):
    border_pen: QPen | None
    border_radius: int | None
    text_stylesheet: str | None
    logger: logging.LoggerAdapter
    
    def __init__(self, label_text: str):
        super().__init__()
        self.logger = CustomLoggerAdapter.getLogger('gui', className='DragNDropLabel')

        layout = QVBoxLayout(self)
        # Create a QLabel for the text
        self.label_text = QLabel(label_text, self)
        # Center the text
        self.label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_text)
        
        self.set_text_style()
        self.set_border_style()
        
    def set_border_style(
        self,
        *,
        border_color: Qt.GlobalColor | QColor | str = DEFAULT_BORDER_COLOR,
        border_style: Qt.PenStyle | list[int] = DEFAULT_BORDER_STYLE,
        border_radius: int = DEFAULT_BORDER_RADIUS,
        border_width: int = DEFAULT_BORDER_WIDTH
    ) -> None:
        self.border_pen = QPen(QColor(border_color), border_width)
        
        if isinstance(border_style, list):
            self.border_pen.setStyle(Qt.PenStyle.CustomDashLine)
            self.border_pen.setDashPattern(border_style)
        else:
            self.border_pen.setStyle(border_style)
            
        self.border_radius = border_radius
            
    
    def set_text_style(
        self,
        *,
        color: Qt.GlobalColor | QColor | str = DEFAULT_TEXT_COLOR,
        font_size: int = DEFAULT_FONT_SIZE,
        font_weight: str = DEFAULT_FONT_WEIGHT,
        font_family: str = DEFAULT_FONT_FAMILY
    ) -> None:
        self.text_stylesheet = \
            f'color: {QColor(color).name(QColor.NameFormat.HexRgb)};' \
            f'font-size: {font_size}px;' \
            f'font-weight: {font_weight};' \
            f'font-family: {font_family};'
        self.label_text.setStyleSheet(self.text_stylesheet)
            
        
    def paintEvent(self, _: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        border = self.rect().translated(self.border_pen.width(), self.border_pen.width())
        border.setBottomRight(QPoint(
            border.bottomRight().x() - 2 * self.border_pen.width(),
            border.bottomRight().y() - 2 * self.border_pen.width()
        ))

        # Draw the rounded border
        painter.setPen(self.border_pen)
        painter.drawRoundedRect(border, self.border_radius, self.border_radius)


class AddDataFromFile(MainWindow):
    logger: logging.LoggerAdapter
    main_widget: QWidget
    main_layout: QVBoxLayout
    drag_n_drop_label: DragNDropLabel
    
    def __init__(self, parent: Any | None = None):
        super().__init__(parent)
        self.logger = CustomLoggerAdapter.getLogger('gui', className='AddDataFromFile')
        
        self.setWindowTitle("Budgeting App - Add Data From File")
        
        self.window_width, self.window_height = 500, 400
        self.setFixedSize(self.window_width, self.window_height)
        
        self.setAcceptDrops(True)
        
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        self.drag_n_drop_label = DragNDropLabel("Drag'n'drop CSV,\nPDF or JSON files\nhere.")
        self.drag_n_drop_label.setGeometry(
            int((self.window_width - 200) / 2),
            int((self.window_height - 200) / 2),
            200,
            200
        )
        self.main_layout.addWidget(self.drag_n_drop_label)
        
        self.setCentralWidget(self.main_widget)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
            
        self.logger.debug(f'Got event.mimeData.urls={event.mimeData().urls()}')
        
        if event.mimeData().hasUrls():
            if [qurl.toLocalFile() for qurl in event.mimeData().urls()][0].endswith(RECOGNISED_FILETYPES):
                
                event.accept()
                self.logger.debug('QDragEnterEvent accepted.')
                
                return None
            
            self.logger.info(f'Unrecognised file extension: \'.{[qurl.toLocalFile() for qurl in event.mimeData().urls()][0].split(".")[-1]}\'')
        
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        
        # take only the first one
        filepath = files[0]
        self.logger.info(f'Got file: \'{filepath.split("/")[-1]}\'')
        
        if filepath.endswith('.pdf'):
            
            pdf_file_wrapper = PDFReader.open(filepath=filepath)
                
            if pdf_file_wrapper is not None:
                
                ServiceManager.service_attr(ServiceManager.ServiceName.TABLE_EXTRACTOR, 'set_table_detector_workspace', pdf_file_wrapper=pdf_file_wrapper)
                ServiceManager.run(ServiceManager.ServiceName.TABLE_EXTRACTOR)
                event.accept()
                
            else:
                self.logger.warning(f'pdf_file_wrapper is None.')
                
        elif filepath.endswith('.csv'):
            ServiceManager.service_attr(ServiceManager.ServiceName.CSV_TABLE_EXTRACTOR, 'add_data_from_file', filepath=filepath)
            ServiceManager.run(ServiceManager.ServiceName.CSV_TABLE_EXTRACTOR)
            event.accept()
        elif filepath.endswith('.json'):
            ServiceManager.service_attr(ServiceManager.ServiceName.JSON_TABLE_EXTRACTOR, 'add_data_from_file', filepath=filepath)
            ServiceManager.run(ServiceManager.ServiceName.JSON_TABLE_EXTRACTOR)
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    select_profile = AddDataFromFile()
    select_profile.show()
    sys.exit(app.exec())
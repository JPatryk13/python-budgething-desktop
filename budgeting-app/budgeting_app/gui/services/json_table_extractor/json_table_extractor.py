from typing import Any
import logging

from budgeting_app.gui.services.base import MainWindow
from budgeting_app.utils.logging import CustomLoggerAdapter


class JSONTableExtractor(MainWindow):
    
    logger: logging.LoggerAdapter

    def __init__(self, parent: Any | None = None):
        super().__init__(parent)
        self.setWindowTitle("Budgeting App - JSON Table Extractor")
        # self.setGeometry(self.window_default_geometry)
        
        self.logger = CustomLoggerAdapter.getLogger('gui', className='JSONTableExtractor')
        self.logger.info('Initialising JSONTableExtractor.')
        
    def add_data_from_file(self, filepath: str) -> None:
        pass

import sys

from PyQt6.QtWidgets import QApplication

from budgeting_app.gui.services.base import ServiceManager
from budgeting_app.gui.services.add_profile.add_profile import AddProfileForm
from budgeting_app.gui.services.csv_table_extractor.csv_table_extractor import CSVTableExtractor
from budgeting_app.gui.services.json_table_extractor.json_table_extractor import JSONTableExtractor
from budgeting_app.gui.services.table_extractor.table_extractor import TableExtractor
from budgeting_app.gui.services.drag_n_drop.drag_n_drop import AddDataFromFile
from budgeting_app.utils.logging import CustomLoggerAdapter, set_up_logging


if __name__ == "__main__":
    set_up_logging()
    app = QApplication(sys.argv)
    ServiceManager.add_services(
        {
            ServiceManager.ServiceName.ADD_PROFILE_FORM: AddProfileForm(),
            ServiceManager.ServiceName.ADD_DATA_FROM_FILE: AddDataFromFile(),
            ServiceManager.ServiceName.TABLE_EXTRACTOR: TableExtractor(),
            ServiceManager.ServiceName.CSV_TABLE_EXTRACTOR: CSVTableExtractor(),
            ServiceManager.ServiceName.JSON_TABLE_EXTRACTOR: JSONTableExtractor()
        }
    )
    ServiceManager.run(ServiceManager.ServiceName.ADD_DATA_FROM_FILE)
    CustomLoggerAdapter.getLogger('gui').info('Application started.')
    sys.exit(app.exec())
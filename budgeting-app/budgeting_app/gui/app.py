import sys

from PyQt6.QtWidgets import QApplication

from budgeting_app.gui.services.base import ServiceManager
from budgeting_app.gui.services.add_profile.add_profile import AddProfileForm
from budgeting_app.gui.services.table_extractor.table_extractor import TableExtractor
from budgeting_app.gui.services.drag_n_drop.drag_n_drop import AddDataFromFile

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ServiceManager.add_services(
        {
            ServiceManager.ServiceName.ADD_PROFILE_FORM: AddProfileForm(),
            ServiceManager.ServiceName.ADD_DATA_FROM_FILE: AddDataFromFile(),
            ServiceManager.ServiceName.TABLE_EXTRACTOR: TableExtractor(),
        }
    )
    ServiceManager.run(ServiceManager.ServiceName.ADD_PROFILE_FORM)
    sys.exit(app.exec())
import logging
import sys
from typing import Any, Generator

from behave import runner, fixture, use_fixture, model, model_core
from PyQt6 import QtWidgets, QtCore

from budgeting_app.gui.services.add_profile.add_profile import AddProfileForm
from budgeting_app.gui.services.base import ServiceManager
from budgeting_app.gui.services.csv_table_extractor.csv_table_extractor import CSVTableExtractor
from budgeting_app.gui.services.drag_n_drop.drag_n_drop import AddDataFromFile
from budgeting_app.gui.services.json_table_extractor.json_table_extractor import JSONTableExtractor
from budgeting_app.gui.services.table_extractor.table_extractor import TableExtractor
from budgeting_app.integration_tests.features.utils import _context
from budgeting_app.utils.logging import set_up_logging, CustomLoggerAdapter


@fixture
def app_fixture(context: _context) -> Generator[QtWidgets.QApplication, Any, None]:
    context.app = QtWidgets.QApplication(sys.argv)
    yield context.app
    context.app.quit()


def before_all(context: _context) -> None:
    
    set_up_logging(global_level='INFO')
    context.logger = CustomLoggerAdapter.getLogger('integration_tests')
    context.logger.info('Setting up environment.')
    
    use_fixture(app_fixture, context)
    
def before_scenario(context: _context, scenario: model.Scenario) -> None:
    context.service_manager_cls = ServiceManager
    context.service_manager_cls.add_services(
        {
            ServiceManager.ServiceName.ADD_PROFILE_FORM: AddProfileForm(),
            ServiceManager.ServiceName.ADD_DATA_FROM_FILE: AddDataFromFile(),
            ServiceManager.ServiceName.TABLE_EXTRACTOR: TableExtractor(),
            ServiceManager.ServiceName.CSV_TABLE_EXTRACTOR: CSVTableExtractor(),
            ServiceManager.ServiceName.JSON_TABLE_EXTRACTOR: JSONTableExtractor()
        }
    )
    context.mouse_event_data = {}
    
def after_step(context: _context, step: model.Step) -> None:
    if step.status in [model_core.Status.untested, model_core.Status.skipped]:
        context.logger.warning(f'### UNTESTED/SKIPPED')
    elif step.status == model_core.Status.passed:
        context.logger.info(f'### PASSED in {step.duration}s')
    elif step.status in [model_core.Status.failed, model_core.Status.undefined]:
        context.logger.error(f'### FAILED/UNDEFINED')
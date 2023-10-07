from pathlib import Path
import os
from behave import given, then, model

from budgeting_app.gui.services.base import ServiceManager
from budgeting_app.integration_tests.features.utils import _context, get_service_by_name
from budgeting_app.pdf_table_reader.core.usecases.pdf_reader import PDFReader

# region: Given

@given('I have the "{service_name}" window open')
def step_impl(context: _context, service_name: str) -> None:
    
    context.current_service_window_obj, context.current_service_name = get_service_by_name(context, service_name)
    
    if  context.current_service_name == ServiceManager.ServiceName.TABLE_EXTRACTOR:
        # Table extractor requires PDFFileWrapper
        if context.filepath.endswith('.pdf'):
            # Correct filepath
            pdf_file_wrapper = PDFReader.open(filepath=context.filepath)
            if pdf_file_wrapper is not None:
                # Managed to open the file
                ServiceManager.service_attr(
                    ServiceManager.ServiceName.TABLE_EXTRACTOR,
                    'set_table_detector_workspace',
                    pdf_file_wrapper=pdf_file_wrapper
                )
            else:
                context.logger.error(f'PDFFileWrapper is None.')
                raise Exception(f'PDFFileWrapper is None.')
        else:
            context.logger.error(f'Wrong filepath supplied. Expected PDF file.')
            raise Exception(f'Wrong filepath supplied. Expected PDF file.')


    # Launch the requested service and write its name to the context for future reference
    context.logger.info(f'Running {service_name}.')
    context.service_manager_cls.run(context.current_service_name)

@given('I have a valid {filename} file')
def step_impl(context: _context, filename: str) -> None:
    
    # create str filepath from the filename
    context.filepath = str(Path(__file__).parent.parent.parent / 'data' / filename)
    
    if os.path.exists(context.filepath):
        context.logger.debug(f'Path exists: {context.filepath}.')
    else:
        context.logger.error(f'Given path is not valid: {context.filepath}.')
        raise Exception(f'Given path is not valid: {context.filepath}.')
        
@given('the data are')
def step_impl(context: _context) -> None:
    
    # Convert model.Table object to a simple list of lists
    table: model.Table = context.table
    context.table_data = [table.headings]
    for row in table:
        context.table_data.append([row[col_name] for col_name in table.headings])
            
# endregion

# region: Then

@then('"{service_name_str}" is opened')
@then('"{service_name_str}" is open')
def step_impl(context: _context, service_name_str: str) -> None:
    
    context.current_service_window_obj, context.current_service_name = get_service_by_name(context, service_name_str)
    
    assert context.current_service_window_obj.isVisible()

# endregion
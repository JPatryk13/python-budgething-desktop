import logging
from typing import Any, TypeVar, TypedDict

from behave import runner
from PyQt6 import QtCore, QtWidgets

from budgeting_app.gui.services.base import ServiceManager

class _context(runner.Context):
    app: QtWidgets.QApplication
    service_manager_cls: ServiceManager
    current_service_name: ServiceManager.ServiceName
    current_service_window_obj: QtWidgets.QMainWindow
    event: QtCore.QEvent | None
    filepath: str
    logger: logging.LoggerAdapter
    table_data: list[list[str | None]]
    previous_image_size: QtCore.QSize
    mouse_event_data: 'mouseEvent.data'
    
    class mouseEvent:
        class data(TypedDict, total=False):
            mouseMoveEvent: '_context.mouseEvent.move'
            mouseReleaseEvent: '_context.mouseEvent.release'
            mousePressEvent: '_context.mouseEvent.press'
                
        class move(TypedDict):
            widget: QtWidgets.QWidget
            step_size: tuple[float, float]
            coursor_path: list[tuple[float, float]]
            image_origin_start_pos: tuple[float, float]
            image_origin_path: list[tuple[float, float]]
            
        class release(TypedDict):
            widget: QtWidgets.QWidget
            coursor_pos: tuple[float, float]
            
        class press(TypedDict):
            widget: QtWidgets.QWidget
            coursor_pos: tuple[float, float]
    
    
def get_qwindow_centre(qwindow: QtWidgets.QWidget | QtWidgets.QMainWindow) -> tuple[int, int]:
    return (
        int(qwindow.geometry().x() + qwindow.geometry().width() / 2),
        int(qwindow.geometry().y() + qwindow.geometry().height() / 2)
    )
    
def get_service_by_name(context: _context, service_name: str) -> tuple[QtWidgets.QMainWindow, ServiceManager.ServiceName]:
    """Returns service window object and handles logging and validation.

    Args:
        context (_context): context class used here only for retrieving ServiceManager class and logging
        service_name (str): Name of the service as a string matching values ServiceManager.ServiceName

    Returns:
        QtWidgets.QMainWindow | None: Service window object
        ServiceManager.ServiceName | None: Name of the service as a member of the ServiceName Enum
    """
    try:
        
        _service_name = ServiceManager.ServiceName(service_name)
        
        return get_service_by_ServiceName(context, _service_name), _service_name
        
    except ValueError:
        
        context.logger.error(f'{service_name} is not valid ServiceName member\'s value.')
        raise ValueError(f'{service_name} is not valid ServiceName member\'s value.')
    
def get_service_by_ServiceName(context: _context, service_name: ServiceManager.ServiceName) -> QtWidgets.QMainWindow:
    """Returns service window object and handles logging and validation.

    Args:
        context (_context): context class used here only for retrieving ServiceManager class and logging
        service_name (ServiceManager.ServiceName): Name of the service as a member of the ServiceName Enum

    Returns:
        QtWidgets.QMainWindow | None: Service window object
    """
    service_window = context.service_manager_cls.get_service_obj(service_name)
        
    if service_window is not None:
        context.logger.debug(f'ServiceManager.get_service_obj returned {service_window}')
        return service_window
    
    context.logger.error('ServiceManager.get_service_obj returned None.')
    raise Exception('ServiceManager.get_service_obj returned None.')
    
def is_correct_service_used(
    context: _context,
    expected_service_names: ServiceManager.ServiceName | list[ServiceManager.ServiceName],
    error_on_false: bool = True
) -> bool:
    """Check if the service name and object recorded in the context matches the expect one.

    Args:
        context (_context): used to retrieve current_service_name, service_manager_cls,
        current_service_window_obj and logger
        expected_service_names (ServiceManager.ServiceName): Name of the service as a string matching values
        ServiceManager.ServiceName
        error_on_false (bool, optional): If set to False the function will return True/False without raising
        any errors. Defaults to True.

    Raises:
        Exception: When the context.current_service_name doesn't match expected_service_names
        Exception: When the context.current_service_window_obj doesn't match the object inferred as expected
        by the expected_service_names

    Returns:
        bool
        
    Updates:
        29/09/2023: `expected_service_names` can be `list[ServiceManager.ServiceName]`. The function the will
        check for match with eather member of the list.
    """
    # if expected_service_names is not a list convert it to one
    if not isinstance(expected_service_names, list):
        expected_service_names = [expected_service_names]
        
    if context.current_service_name in expected_service_names:
        # context.current_service_name has a correct value
        
        expected_service_objects_types = tuple([type(context.service_manager_cls.get_service_obj(exp)) for exp in expected_service_names])
        
        if isinstance(context.current_service_window_obj, expected_service_objects_types):
            
            return True
        
        else:
            
            err_msg = f'Service object must be a member of {expected_service_objects_types}. ' \
                'Got {type(context.current_service_window_obj)} instead.'
            
            context.logger.error(err_msg)
            
            if not error_on_false:
                return False
            else:
                raise Exception(err_msg)
    else:
        
        err_msg = f'Service name must be a member of {expected_service_names}. ' \
            f'Got {context.current_service_name} instead.'
        
        context.logger.error(err_msg)
        
        if not error_on_false:
            return False
        else:
            raise Exception(err_msg)
        
def is_member_of(context: _context, member: Any, member_name: str, _collection: list[Any], error_on_false: bool = True) -> bool:
    """Validates if a member is part of the list. Handles errors and logging.

    Args:
        context (_context): Used here only for logging
        member (Any): Variable expected to be in the `_collection` list
        member_name (str): Name of the variable, used from log/error messages
        _collection (list[Any]): List of elements of the same type as the property `member`
        error_on_false (bool, optional): If set to False the function will return True/False without raising
        any errors. Defaults to True.

    Raises:
        Exception: When the `member` is not in the `_collection`

    Returns:
        bool
    """
    if member in _collection:
        
        return True
    
    else:
        
        context.logger.error(f'{member_name} must be part of {_collection} list.')
        
        if not error_on_false:
            return False
        else:
            raise Exception(f'{member_name} must be part of {_collection} list.')
        
def interpolate(start: int, stop: int, *, step_count: int = 0, step: float = 0.0) -> list[float]:
    if step_count == 0 and step == 0.0:
        raise ValueError('Either \'step\' or \'step_count\' are required. Both were found to be 0(.0).')
    
    if step_count == 0:
        step_count = (stop - start) / step
    elif step == 0.0:
        step = (stop - start) / step_count
    else:
        raise ValueError('Both \'step\' and \'step_count\' cannot be specified together.')
        
    return [start + step * i for i in range(int(step_count) + 1)]
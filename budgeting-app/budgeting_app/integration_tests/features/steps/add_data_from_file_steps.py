from behave import when, then
from PyQt6 import QtCore, QtGui

from budgeting_app.integration_tests.features.utils import _context, get_qwindow_centre



# region: When

@when('I {action} the file')
def step_impl(context: _context, action: str) -> None:
    context.logger.info(f'Running \'I {action} the file\'')
    
    # create mime data object from the file
    mime_data = QtCore.QMimeData()
    mime_data.setUrls([QtCore.QUrl.fromLocalFile(context.filepath)])
    context.logger.debug(f'Got mime_data={mime_data}')
    
    _drag_event = 'drag' in action.lower()
    _drop_event = 'drop' in action.lower()
    _info_str: list[str] = []
    _events: list[QtCore.QEvent] = []
    
    if _drag_event:
        # create a QDragEnterEvent event @ the centre of the window
        context.event = QtGui.QDragEnterEvent(
            QtCore.QPoint(*get_qwindow_centre(context.current_service_window_obj)),
            QtCore.Qt.DropAction.MoveAction,
            mime_data,
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        _events.append(context.event)
        _info_str.append('QDragEnterEvent')
        
    if _drop_event:
        # create a QDropEvent event @ the centre of the window - we only
        # need to preserve the last one (drop) in the context (assumning
        # that both are requested)
        context.event = QtGui.QDropEvent(
            QtCore.QPointF(*get_qwindow_centre(context.current_service_window_obj)),
            QtCore.Qt.DropAction.CopyAction,
            mime_data,
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifier.NoModifier,
            QtCore.QEvent.Type.Drop
        )
        _events.append(context.event)
        _info_str.append('QDropEvent')
        
    context.logger.debug(f'Sending {_info_str} to {context.current_service_name.value}')
    # send the event to the service
    for e in _events:
        QtCore.QCoreApplication.sendEvent(context.current_service_window_obj, e)

# endregion

# region: Then

@then('I see that it is {is_accepted} filetype')
@then('The file is {is_accepted}')
def step_impl(context: _context, is_accepted: str) -> None:
    context.logger.info(f'Running \'I see that it is {is_accepted} filetype\' or \'The file is {is_accepted}\'')
    
    _is_accepted = 'not' not in is_accepted
    assert context.event.isAccepted() == _is_accepted, f'The event was supposed to be {"" if _is_accepted else "not "}accepted, however, the opposite happened.'

# endregion

import math
from tkinter import Canvas
import typing
import unittest
from PyQt6.QtGui import QPointingDevice
from behave import given, when, then
from PyQt6 import QtWidgets, QtGui, QtCore

from budgeting_app.gui.services.base import ServiceManager
from budgeting_app.integration_tests.features.utils import _context, get_qwindow_centre, interpolate, is_correct_service_used, is_member_of
from budgeting_app.pdf_table_reader.core.entities.models import ImageWrapper

# region: When

@when('I select the "{tool_name}"')
def step_impl(context: _context, tool_name: str) -> None:
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
    
    if tool_name.lower() == 'hand tool':
        context.current_service_window_obj.hand_tool_button.click()
        
        if context.current_service_window_obj.hand_tool_button.isChecked():
            context.logger.debug('Selected hand tool.')
        else:
            context.logger.error('Expected hand tool to be selected however that is not the case.')
        
    elif tool_name.lower() == 'table tool':
        context.current_service_window_obj.table_drawing_tool_button.click()
        
        if context.current_service_window_obj.table_drawing_tool_button.isChecked():
            context.logger.debug('Selected table drawing tool.')
        else:
            context.logger.error('Expected table drawing tool to be selected however that is not the case.')
        
    else:
        context.logger.error(f'tool_name must be either "hand tool" or "table tool". Got {tool_name.lower()} instead.')
        
@when('I move the mouse scroll "{direction}" within "{widget_name}"')
def step_impl(context: _context, direction: str, widget_name: str) -> None:
    
    # check if the widget name is valid
    if context.current_service_name == ServiceManager.ServiceName.TABLE_EXTRACTOR:
        if widget_name == 'image viewer':
            tab_idx = context.current_service_window_obj.image_viewer.current_tab
            # Get Canvas object from current tab 
            widget: QtWidgets.QMainWindow = context.current_service_window_obj.image_viewer.tabs[tab_idx]
            # Record the image size from the Canvas
            context.previous_image_size = widget.image_data.current_scaled_image.size()
        else:
            raise NotImplementedError
            
    if direction.lower() in ['forward', 'backward']:
        # Scroll direction is valid
        
        angle_delta_modifier = 1 if direction.lower() == 'forward' else -1
        
        context.event = QtGui.QWheelEvent(
            QtCore.QPointF(widget.width() / 2, widget.height() / 2),
            widget.mapToGlobal(QtCore.QPointF(widget.width() / 2, widget.height() / 2)),
            QtCore.QPoint(),
            QtCore.QPoint(0, angle_delta_modifier * 120),
            QtCore.Qt.MouseButton.NoButton,
            QtCore.Qt.KeyboardModifier.NoModifier,
            QtCore.Qt.ScrollPhase.NoScrollPhase,
            False
        )
        context.logger.debug(f'Sending {context.event} to the {widget} widget.')
        
        QtCore.QCoreApplication.sendEvent(widget, context.event)
        
    else:
        context.logger.error(f'Scroll driection can only be "forward" or "backward". Got {direction.lower()} instead.')
        raise Exception(f'Scroll driection can only be "forward" or "backward". Got {direction.lower()} instead.')
        
@when('I hold "{button_identifier}" and drag the coursor within "{widget_name}" from "{start_pos_identifier}" "{translation_identifier}"')
def step_impl(
    context: _context,
    button_identifier: str,
    widget_name: str,
    start_pos_identifier: str,
    translation_identifier: str
) -> None:
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
    # validate button_identifier
    is_member_of(context, button_identifier, 'button_identifier', ['left mouse button'])
    # validate widget_name
    is_member_of(context, widget_name, 'widget_name', ['image viewer', 'canvas'])
    # validate start_pos_identifier
    is_member_of(context, start_pos_identifier, 'start_pos_identifier', ['centre'])
    # validate translation_identifier
    is_member_of(context, translation_identifier, 'translation_identifier', ['to left'])
    
    if button_identifier == 'left mouse button':
         # I'm populating the event with that one
        btn = QtCore.Qt.MouseButton.LeftButton
    else:
        raise NotImplementedError
    
    if widget_name == 'image viewer':
        tab_idx = context.current_service_window_obj.image_viewer.current_tab
        # Get Canvas object from the current tab 
        widget: Canvas = context.current_service_window_obj.image_viewer.tabs[tab_idx]
    else:
        raise NotImplementedError
    
    if start_pos_identifier == 'centre':
        # find centre of the widget
        start_pos = get_qwindow_centre(widget)
    else:
        raise NotImplementedError
    
    if translation_identifier == 'to left':
        # find left boundary of the widget
        end_pos = (int(widget.geometry().left()), start_pos[1])
    else:
        raise NotImplementedError
    
    # Create a list of touples where each one is populated with x, y values
    # of the corresponding position of the coursor - theposition is determined
    # by interpolating between the start_po and end_pos
    _path = list(zip(
        interpolate(start_pos[0], end_pos[0], step_count=100),
        interpolate(start_pos[1], end_pos[1], step_count=100)
    ))
    start_pos = _path[0]
    path = _path[1:]
    
    
    # create, save and send the mousePressEvent
    press_event_data: _context.mouseEvent.press = {
        'widget': widget,
        'coursor_pos': start_pos
    }
    context.mouse_event_data['mousePressEvent'] = press_event_data
    context.event = QtGui.QMouseEvent(
        QtCore.QEvent.Type.MouseButtonPress,
        QtCore.QPointF(*start_pos),
        btn,
        btn,
        QtCore.Qt.KeyboardModifier.NoModifier
    )
    QtCore.QCoreApplication.sendEvent(widget, context.event)
    
    # create and save to the context the mouseMoveEvent data
    move_event_data: _context.mouseEvent.move = {
        'widget': widget,
        'step_size': (path[1][0] - path[0][0], path[1][1] - path[0][1]),
        'coursor_path': path,
        'image_origin_start_pos': (widget.image_data.current_origin_pos.x(), widget.image_data.current_origin_pos.y()),
        'image_origin_path': []
    }
    context.mouse_event_data['mouseMoveEvent'] = move_event_data
    
    # for each x-y pair send a QMouseMove event to tht widget
    for x, y in path:
        context.event = QtGui.QMouseEvent(
            QtCore.QEvent.Type.MouseMove,
            QtCore.QPointF(x, y),
            btn,
            btn,
            QtCore.Qt.KeyboardModifier.NoModifier
        )
        
        # appended before the event is sent
        context.mouse_event_data['mouseMoveEvent']['image_origin_path'].append((widget.image_data.current_origin_pos.x(), widget.image_data.current_origin_pos.y()))
        QtCore.QCoreApplication.sendEvent(widget, context.event)
    
@when('I release the "{button_identifier}"')
def step_impl(context: _context, button_identifier: str) -> None:
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
    # validate button_identifier
    is_member_of(context, button_identifier, 'button_identifier', ['left mouse button'])
    
    if button_identifier == 'left mouse button':
        # I'm populating the event with that one
        btn = QtCore.Qt.MouseButton.LeftButton
    else:
        raise NotImplementedError
    
    # We want to check if the previous event was click or move and
    # accordingly extract the position from the previous event
    if 'mouseMoveEvent' in context.mouse_event_data.keys():
        previous_mouse_event = 'mouseMoveEvent'
        coursor_pos = context.mouse_event_data[previous_mouse_event]['coursor_path'][-1]
    elif 'mousePressEvent' in context.mouse_event_data.keys():
        previous_mouse_event = 'mousePressEvent'
        coursor_pos = context.mouse_event_data[previous_mouse_event]['coursor_pos']
    else:
        raise Exception(f'\'mouseMoveEvent\' or \'mousePressEvent\' must be already present in the context.mouse_event_data.keys() = {context.mouse_event_data.keys()}.')
    
    context.event = QtGui.QMouseEvent(
        QtCore.QEvent.Type.Move,
        QtCore.QPointF(*coursor_pos),
        btn,
        btn,
        QtCore.Qt.KeyboardModifier.NoModifier
    )
    
    context.mouse_event_data['mouseReleaseEvent'] = {
        'widget': context.mouse_event_data[previous_mouse_event]['widget'],
        'coursor_pos': coursor_pos
    }
    QtCore.QCoreApplication.sendEvent(context.mouse_event_data['mouseReleaseEvent']['widget'], context.event)
    
# endregion

# region: Then
    
@then('the number of displayed tabs is {tab_count:d}')
def step_impl(context: _context, tab_count: int):
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
    
    assert len(context.current_service_window_obj.image_viewer.tabs) == tab_count, \
        f'Expected {tab_count} tab(s), got {len(context.current_service_window_obj.image_viewer.tabs)} instead.'

@then('I can see my data in the table widget')
def step_impl(context: _context):
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
        
    table_widget: QtWidgets.QTableWidget = getattr(context.current_service_window_obj, 'table_widget', None)
    
    if table_widget is not None:

        actual = []
        for row_idx in range(table_widget.rowCount()):
            row_data = []
            for col_idx in range(table_widget.columnCount()):
                item = table_widget.item(row_idx, col_idx)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append(None)
            actual.append(row_data)
            
        assert actual == context.table_data, \
            f'''
            actual={actual},\n
            expected={context.table_data}
            '''
            
    else:
        context.logger.error('Cannot find table_widget')
        
@then('the "{tool_name}" is selected')
def step_impl(context: _context, tool_name: str) -> None:
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
    # validate tool_name
    is_member_of(context, tool_name, 'tool_name', ['hand tool', 'table tool'])
        
    current_tab_idx = context.current_service_window_obj.image_viewer.current_tab
    is_drawing_enabled = context.current_service_window_obj.image_viewer.tabs[current_tab_idx].is_drawing_enabled
    
    assert is_drawing_enabled == (tool_name.lower() == 'table tool'), \
        f'''
        Expected is_drawing_enabled in currently used Canvas object to be
        {(tool_name.lower() == 'table tool')}, however found that it is {is_drawing_enabled}
        '''
        
    table_tool_btn: QtWidgets.QPushButton = context.current_service_window_obj.table_drawing_tool_button
    hand_tool_btn: QtWidgets.QPushButton = context.current_service_window_obj.hand_tool_button
    
    assert table_tool_btn.isChecked() == (tool_name.lower() == 'table tool'), \
        f'''
        table_tool_btn:
            expected:
                isChecked = {(tool_name.lower() == 'table tool')}
            acctual:
                isChecked = {table_tool_btn.isChecked()}
        '''
        
    assert hand_tool_btn.isChecked() == (tool_name.lower() == 'hand tool'), \
        f'''
        hand_tool_btn:
            expected:
                isChecked = {(tool_name.lower() == 'hand tool')}
            acctual:
                isChecked = {hand_tool_btn.isChecked()}
        '''

@then('the image "{image_behavior}"')
def step_impl(context: _context, image_behavior: str) -> None:
    
    # check if we are using this step in the right context
    is_correct_service_used(context, ServiceManager.ServiceName.TABLE_EXTRACTOR)
    # validate comparative_size
    is_member_of(
        context,
        image_behavior,
        'comparative_size',
        [
            'becomes bigger',
            'becomes larger',
            'becomes smaller',
            'moves with the coursor',
            'remains in its position'
        ]
    )
    
    if image_behavior in ['becomes bigger', 'becomes larger', 'becomes smaller']:
        
        # check if the previous size of the image is available
        if getattr(context, 'previous_image_size', None) is None:
            context.logger.error(f'context.previous_image_size is None but it is required to run this step.')
        
        # find current size of the image as is displayed
        current_tab_idx = context.current_service_window_obj.image_viewer.current_tab
        current_img_size: QtCore.QSize = context.current_service_window_obj.image_viewer.tabs[current_tab_idx].image_data.current_scaled_image.size()
        
        if image_behavior in ['becomes bigger', 'becomes larger']:
            
            assert current_img_size.width() > context.previous_image_size.width() and \
                current_img_size.height() > context.previous_image_size.height(), \
                f'''
                Current size of the image was expected to be larger than the original.
                Expected > {context.previous_image_size}
                Actual = {current_img_size}
                '''
                
        else:  # image_behavior='becomes smaller'
            
            assert current_img_size.width() < context.previous_image_size.width() and \
                current_img_size.height() < context.previous_image_size.height(), \
                f'''
                Current size of the image was expected to be smaller than the original.
                Expected < {context.previous_image_size}
                Actual = {current_img_size}
                '''
                
    elif image_behavior in ['moves with the coursor', 'remains in its position']:
        
        if image_behavior == 'moves with the coursor':
            # check if the image coordinates change by the same amount
            if 'mouseMoveEvent' not in context.mouse_event_data.keys():
                raise Exception('\'mouseMoveEvent\' dict in context.mouse_event_data is required when image_behavior=\'moves with the coursor\'.')
            
            coursor_path = context.mouse_event_data['mouseMoveEvent']['coursor_path']
            image_path = context.mouse_event_data['mouseMoveEvent']['image_origin_path']
            
            for i, ((coursor_pos_x, coursor_pos_y), (img_opos_x, img_opos_y)) in enumerate(list(zip(coursor_path, image_path))):
                if i < len(coursor_path) - 1:
                    (next_coursor_pos_x, next_coursor_pos_y), (next_img_opos_x, next_img_opos_y) = list(zip(coursor_path, image_path))[i + 1]
                    
                    delta_coursor_pos_x = next_coursor_pos_x - coursor_pos_x
                    delta_coursor_pos_y = next_coursor_pos_y - coursor_pos_y
                    delta_img_opos_x = next_img_opos_x - img_opos_x
                    delta_img_opos_y = next_img_opos_y - img_opos_y
                    
                    coursor_disp = math.sqrt(delta_coursor_pos_x ** 2 + delta_coursor_pos_y ** 2)
                    img_odisp = math.sqrt(delta_img_opos_x ** 2 + delta_img_opos_y ** 2)
                    
                    # Check if coursor displacement and image origin displacement are almost the same
                    unittest.TestCase().assertAlmostEqual(coursor_disp, img_odisp, 1)
                    
                    y_to_x_ratio: typing.Callable[[float, float], float] = lambda y, x: y * math.inf if float(x) == 0.0 else y/x
                    delta_angle: typing.Callable[[float, float, float, float], float] = lambda y1, x1, y2, x2: math.atan(y_to_x_ratio(y1, x1)) - math.atan(y_to_x_ratio(y2, x2))
                    
                    
                    delta_coursor_pos_angle = delta_angle(coursor_pos_x, coursor_pos_y, next_coursor_pos_x, next_coursor_pos_y)
                    delta_img_opos_angle = delta_angle(img_opos_x, coursor_pos_y, next_coursor_pos_x, next_coursor_pos_y)
                    
                    # Check if the coursor and image origin angle (of the line drawn from the origin
                    # of the plane to the respective point) change are approximately the same
                    unittest.TestCase().assertAlmostEqual(delta_coursor_pos_angle, delta_img_opos_angle, 1)
            
        else:  # image_behavior='remains in its position'
            pass

# endregion
from dataclasses import dataclass
import enum
import sys
from typing import Any

from PyQt6 import QtWidgets, QtCore, QtGui


class ServiceManager:
    """Bridge between services to avoid circular imports and code duplication.
    """
    
    
    class __NoServicesException(Exception):
        """Raised when `self.services` is empty
        """
        def __init__(self, *args: object) -> None:
            super().__init__('Services must be added prior to any operations. It can be done via add_services() method.', *args)
    
    
    class __MissingRequiredServicesException(Exception):
        """Raised when any of the required services is missing
        """
        def __init__(self, expected: list[str], actual: list[str], *args: object) -> None:
            super().__init__(f'Required services are: {expected}. Got {actual} instead.', *args)
    
    
    class __ServiceMethodNotFound(Exception):
        """Raised when the given service doesn't have the requested method
        """
        def __init__(self, service_name: 'ServiceManager.ServiceName', method_name: str, *args: object) -> None:
            super().__init__(f'Service {service_name.value} doesn\'t have a method {method_name}.', *args)
            
    class __InvalidKwargs(Exception):
        """Raised when the given service attribute does not accept given kwargs
        """
        def __init__(self, service_name: 'ServiceManager.ServiceName', method_name: str, _kwargs: dict, *args: object) -> None:
            super().__init__(f'{service_name.value}\'s method {method_name} doesn\'t accept kwargs, {_kwargs}', *args)
    
    
    class ServiceName(enum.Enum):
        ADD_PROFILE_FORM = 'AddProfileForm'
        ADD_DATA_FROM_FILE = 'AddDataFromFile'
        TABLE_EXTRACTOR = 'TableExtractor'
    
    
    @dataclass
    class Service:
        name: 'ServiceManager.ServiceName'
        obj: QtWidgets.QMainWindow
        is_active: bool
        
        
    services: list[Service] = []

    @classmethod    
    def add_services(cls, _services: dict[ServiceName, QtWidgets.QMainWindow]) -> None:
        """All registered (within that class) services must be added at once. Upon each run
        of the method old value of `cls.servies` is replaced by the new one.

        Args:
            _services (dict[ServiceName, QtWidgets.QMainWindow]): exmaple:
            ```
            _services = {
                ServiceManager.ServiceName.ADD_PROFILE_FORM: AddProfileForm(),
                ServiceManager.ServiceName.ADD_DATA_FROM_FILE: AddDataFromFile(),
                ServiceManager.ServiceName.TABLE_EXTRACTOR: TableExtractor(),
            }
            ```
            Each value of the input inherits from MainWindow base class which inherits from
            QtWidgets.QMainWindow.

        Raises:
            __MissingRequiredServicesException
        """
        if set(cls.ServiceName) == set(_services.keys()):
            cls.services = [cls.Service(name=k, obj=v, is_active=False) for k, v in _services.items()]
        else:
            cls.__MissingRequiredServicesException([s.value for s in cls.ServiceName], list(_services.keys()))

    @classmethod    
    def has_services(cls) -> bool:
        return cls.services != []

    @classmethod    
    def run(cls, service_name: ServiceName) -> None:
        """Runs `QtWidgets.QMainWindow.show()` on the instance of the service object and sets
        `cls.services[i].is_active` to `True` for that given service. Other ones are treated
        the opposite.

        Args:
            service_name (ServiceName): Service for which the method `QtWidgets.QMainWindow.show()`
            needs to run and the value `cls.services[i].is_active` set to True.
            
        Raises:
            __NoServicesException
        """
        print(f'running: ServiceManager.run with service_name={service_name}')
        if cls.has_services():
            for i, serv in enumerate(cls.services):
                
                # debug
                if service_name == cls.ServiceName.ADD_PROFILE_FORM and serv.name == service_name:
                    print(f'\tservice.name={serv.name}')
                    print(f'\tservice.obj={serv.obj}')
                    print(f'\tservice.is_active={serv.is_active}')
                
                if serv.name == service_name and not serv.is_active:
                    serv.obj.show()
                    cls.services[i].is_active = True
                elif serv.name != service_name and serv.is_active:
                    serv.obj.close()
                    cls.services[i].is_active = False
        else:
            cls.__NoServicesException()

    @classmethod    
    def service_attr(cls, service_name: ServiceName, attr_name: str, call: bool = True, **kwargs) -> Any | None:
        """Run `attr_name` method on `service_name` service. 
        
        Example:
            service_name: `ServiceName.SOME_SERVICE` -> actual_service_instance: `SomeService()`
            attr_name: `'some_func'`
            kwargs: `param1='foo'`, `param2='bar'`
            
            Translates to: `SomeService().some_func(param1='foo', param2='bar')`
            
        Args:
            ...
            call (bool): When set to True (default) the attribute of the class is being called with given kwargs

        Returns:
            Any | None: Whatever the run method returns
            
        Raises:
            __InvalidKwargs\n
            __ServiceMethodNotFound\n
            __NoServicesException
        """
        if cls.has_services():
            # service manager has all required services added
            for i, serv in enumerate(cls.services):
                if serv.name == service_name:
                    # found match
                    service_attr = getattr(cls.services[i].obj, attr_name, None)
                    if service_attr is not None:
                        # service attribute exists
                        if call:
                            try:
                                return service_attr(**kwargs)
                            except:
                                cls.__InvalidKwargs(service_name, attr_name, kwargs)
                        else:
                            return service_attr
                    else:
                        cls.__ServiceMethodNotFound(service_name, attr_name)
        else:
            cls.__NoServicesException()

    @classmethod            
    def service_is_active(cls, service_name: ServiceName) -> None:
        for serv in cls.services:
            if serv.name == service_name:
                return serv.is_active

    @classmethod        
    def get_service_obj(cls, service_name: ServiceName) -> None:
        for serv in cls.services:
            if serv.name == service_name:
                return serv.obj
            

class MainWindow(QtWidgets.QMainWindow):
    
    window_default_geometry = QtCore.QRect(100, 100, 1200, 675)

    # These actions are the most top toolbar with Profile/Data/Help options
    dashboard_action: QtGui.QAction
    dummy_profile_action: QtGui.QAction
    demo_profile_action: QtGui.QAction
    add_profile_action: QtGui.QAction
    add_transaction_action: QtGui.QAction
    add_bank_account_action: QtGui.QAction
    add_transaction_category_action: QtGui.QAction
    add_transaction_type_action: QtGui.QAction
    add_data_from_file_action: QtGui.QAction
    view_data_action: QtGui.QAction
    about_action: QtGui.QAction

    def __init__(self, parent: Any | None = None):
        super().__init__(parent)
        self.setWindowTitle("Budgeting App")
        self.setGeometry(self.window_default_geometry)
        
        self._create_menu_actions()
        self._create_menu_bar()
        
    def _create_menu_bar(self):
        menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(menu_bar)

        profile_menu = menu_bar.addMenu("Profile")
        profile_menu.addAction(self.dashboard_action)
        # Select profile sub-menu
        select_profile_menu = profile_menu.addMenu("Select profile")
        select_profile_menu.addAction(self.dummy_profile_action)
        select_profile_menu.addAction(self.demo_profile_action)
        select_profile_menu.addSeparator()
        select_profile_menu.addAction(self.add_profile_action)

        data_menu = menu_bar.addMenu("Data")
        data_menu.addAction(self.add_data_from_file_action)
        data_menu.addAction(self.view_transactions_data_action)
        # Add data from file sub-menu
        add_data_menu = data_menu.addMenu("Add data")
        add_data_menu.addAction(self.add_transaction_action)
        add_data_menu.addAction(self.add_bank_account_action)
        add_data_menu.addAction(self.add_transaction_category_action)
        add_data_menu.addAction(self.add_transaction_type_action)
        
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)

    def _create_menu_actions(self) -> None:
        self.dashboard_action = QtGui.QAction('Dashboard', self)
        
        self.dummy_profile_action = QtGui.QAction("dummy_profile", self)
        self.demo_profile_action = QtGui.QAction("Demo Profile", self)
        
        self.add_profile_action = QtGui.QAction("Add Profile", self)
        self.add_profile_action.triggered.connect(lambda: ServiceManager.run(ServiceManager.ServiceName.ADD_PROFILE_FORM))
        
        self.add_transaction_action = QtGui.QAction('Transaction', self)
        self.add_bank_account_action = QtGui.QAction('Bank Account', self)
        self.add_transaction_category_action = QtGui.QAction('Transaction Category', self)
        self.add_transaction_type_action = QtGui.QAction('Transaction Type', self)
        
        self.add_data_from_file_action = QtGui.QAction('Add data from file', self)
        self.add_data_from_file_action.triggered.connect(lambda: ServiceManager.run(ServiceManager.ServiceName.ADD_DATA_FROM_FILE))
        
        self.view_transactions_data_action = QtGui.QAction('View Transactions', self)
        self.about_action = QtGui.QAction('About', self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
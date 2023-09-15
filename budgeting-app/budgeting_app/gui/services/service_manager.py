from dataclasses import dataclass
import enum
import sys
from typing import Any

from PyQt6 import QtWidgets


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
        
        
    services: list[Service]
    
    def __init__(self) -> None:
        self.services = []
        
    def add_services(self, _services: dict[ServiceName, QtWidgets.QMainWindow]) -> None:
        """All registered (within that class) services must be added at once. Upon each run
        of the method old value of `self.servies` is replaced by the new one.

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
        if set(self.ServiceName) == set(_services.keys()):
            self.services = [self.Service(name=k, obj=v, is_active=False) for k, v in _services.items()]
        else:
            self.__MissingRequiredServicesException([s.value for s in self.ServiceName], list(_services.keys()))
        
    def has_services(self) -> bool:
        return self.services != []
        
    def run(self, service_name: ServiceName) -> None:
        """Runs `QtWidgets.QMainWindow.show()` on the instance of the service object and sets
        `self.services[i].is_active` to `True` for that given service. Other ones are treated
        the opposite.

        Args:
            service_name (ServiceName): Service for which the method `QtWidgets.QMainWindow.show()`
            needs to run and the value `self.services[i].is_active` set to True.
            
        Raises:
            __NoServicesException
        """
        print(f'running: ServiceManager.run with service_name={service_name}')
        if self.has_services():
            for i, serv in enumerate(self.services):
                
                # debug
                if service_name == self.ServiceName.ADD_PROFILE_FORM and serv.name == service_name:
                    print(f'\tservice.name={serv.name}')
                    print(f'\tservice.obj={serv.obj}')
                    print(f'\tservice.is_active={serv.is_active}')
                
                if serv.name == service_name and not serv.is_active:
                    serv.obj.show()
                    self.services[i].is_active = True
                elif serv.name != service_name and serv.is_active:
                    serv.obj.close()
                    self.services[i].is_active = False
        else:
            self.__NoServicesException()
        
    def service_attr(self, service_name: ServiceName, attr_name: str, call: bool = True, **kwargs) -> Any | None:
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
        if self.has_services():
            # service manager has all required services added
            for i, serv in enumerate(self.services):
                if serv.name == service_name:
                    # found match
                    service_attr = getattr(self.services[i].obj, attr_name, None)
                    if service_attr is not None:
                        # service attribute exists
                        if call:
                            try:
                                return service_attr(**kwargs)
                            except:
                                self.__InvalidKwargs(service_name, attr_name, kwargs)
                        else:
                            return service_attr
                    else:
                        self.__ServiceMethodNotFound(service_name, attr_name)
        else:
            self.__NoServicesException()
                
    def service_is_active(self, service_name: ServiceName) -> None:
        for serv in self.services:
            if serv.name == service_name:
                return serv.is_active
            
    def get_service_obj(self, service_name: ServiceName) -> None:
        for serv in self.services:
            if serv.name == service_name:
                return serv.obj
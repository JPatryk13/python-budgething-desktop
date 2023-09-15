from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic

from budgeting_app.transaction_management.core.entities.types import T_uuid4_string


T_class = TypeVar('T_class')
T_dict = TypeVar('T_dict')


class CRUDBaseGeneric(Generic[T_class, T_dict], metaclass=ABCMeta):

    @abstractmethod
    def save(self, obj: T_class) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, uuid: T_uuid4_string, data: T_dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, uuid: T_uuid4_string) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_uuid(self, uuid: T_uuid4_string) -> T_class:
        raise NotImplementedError

    @abstractmethod
    def search(self, data: T_dict) -> list[T_class]:
        raise NotImplementedError


T_junction = TypeVar('T_junction')


class JunctionCRUDBaseGeneric(Generic[T_junction], metaclass=ABCMeta):
    @abstractmethod
    def create(self, left: T_uuid4_string, right: T_uuid4_string) -> T_junction:
        raise NotImplementedError

    @abstractmethod
    def save(self, obj: T_junction) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, uuid: T_uuid4_string):
        raise NotImplementedError

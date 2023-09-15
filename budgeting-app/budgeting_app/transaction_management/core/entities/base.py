from dataclasses import dataclass, asdict, field
from uuid import uuid4
from typing import Any, Generic, TypeVar

T_dict = TypeVar('T_dict')


@dataclass
class TagBaseModel(Generic[T_dict]):
    uuid: str = field(compare=False)
    name: str

    def __post_init__(self) -> None:
        self.__validate()

    def __validate(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError

    @classmethod
    def new(cls, name: str):
        return cls(
            uuid=str(uuid4()),
            name=name
        )

    def update(self, param: str, value: Any) -> None:
        if (param in self.to_dict().keys()):
            setattr(self, param, value)
            self.__validate()
        else:
            raise ValueError(
                f'{param} is not a parameter of class {self.__str__()}.')

    def to_dict(self) -> T_dict:
        return asdict(self)

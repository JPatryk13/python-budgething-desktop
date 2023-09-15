import math
import unittest
import inspect
from typing import Any, TypedDict


def euclidean_distance(x1: int | float, x2: int | float, y1: int | float, y2: int | float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def distance_from_line(
    x0: int | float,
    y0: int | float,
    line_x1: int | float,
    line_x2: int | float,
    line_y1: int | float,
    line_y2: int | float,
) -> float:
    line_length = euclidean_distance(line_x1, line_x2, line_y1, line_y2)
    double_traingle_area = abs((line_x2 - line_x1) * (line_y1 - y0) - (line_x1 - x0) * (line_y2 - line_y1))
    return double_traingle_area / line_length

def is_all_not_none(*args: list[Any]) -> bool:
    return all(list(map(lambda val: val is not None, args)))

class InspectMethod:
    
    class Expected(TypedDict, total=False):
        param_name: str
        instance_of: type
        default_value: Any

    @staticmethod
    def param_properties(expected: list[Expected], method_signature: inspect.Signature) -> None:
        
        unittest.TestCase().assertEqual(
            len(expected),
            len(method_signature.parameters.keys()),
            f'Expected {len(expected)} properties, found {len(method_signature.parameters.keys())}'
        )
            
        for i, (param_name, param) in enumerate(method_signature.parameters.items()):
            
            unittest.TestCase().assertEqual(
                param_name,
                expected[i]['param_name'],
                f'param_name={param_name} while expected value is {expected[i]["param_name"]}'
            )
            
            if 'instance_of' in expected[i].keys():
                unittest.TestCase().assertEqual(
                    param.annotation,
                    expected[i]['instance_of'],
                    f'param.annotation={param.annotation} while expected value is {expected[i]["instance_of"]}'
                )
                
            if 'default_value' in expected[i].keys():
                unittest.TestCase().assertEqual(
                    param.default,
                    expected[i]['default_value'],
                    f'param.default={param.default} while expected value is {expected[i]["default_value"]}'
                )
                
    @staticmethod
    def param_names(expected: list[str], method_signature: inspect.Signature) -> None:
        
        unittest.TestCase().assertEqual(
            len(expected),
            len(method_signature.parameters.keys()),
            f'Expected {len(expected)} properties, found {len(method_signature.parameters.keys())}'
        )
        
        for i, param_name in enumerate(method_signature.parameters.keys()):
            
            unittest.TestCase().assertEqual(
                param_name,
                expected[i],
                f'param_name={param_name} while expected value is {expected[i]}'
            )
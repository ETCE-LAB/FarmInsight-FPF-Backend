from typing import NamedTuple, List
from attr import dataclass

from fpf_sensor_service.utils import ListableEnum


'''
The type of a field needs to be correctly validated the same as any rules applying to the field!  
'''
class FieldType(ListableEnum):
    INTEGER = 'int'
    STRING = 'str'


class FieldDescription(NamedTuple):
    id: str
    name: str
    description: str
    type: FieldType
    rules: List[object]
    defaultValue: object = ""


class ValidHttpEndpointRule(NamedTuple):
    pass


class IntRangeRuleInclusive(NamedTuple):
    min: int
    max: int


@dataclass
class ScriptDescription:
    '''
    !!! NEVER CHANGE OR DELETE THE script_class_id, the DB will store them to identify the class !!!
    '''
    script_class_id:str

    '''
    Fields are inputs by the user and are stored as a json dict in the additionalInformation DB column
    '''
    fields: List[FieldDescription]

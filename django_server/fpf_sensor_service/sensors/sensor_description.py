from enum import Enum
from typing import NamedTuple, List

'''
A list of obvious TODOs left:
Correct error propagation to the frontend about errors (looks like atm the backend is just not hading those through correctly) 
A way to have rules already apply in the front end.
colour code tags on the frontend for known tags (info blue, warning orange). Might be overkill and not needed, 
maybe tags should just be instead a simple string even.



BIG ARCHITECTURE QUESTION:

Right now our setup for the classes is a bit basic because every different Connection Type, Parameter and Unit cause 
a new class even in the case like the DHT22 where it's one sensor with 4 classes already.

There are multiple ways to consider, the one easiest on the frontend would be to have multiple SensorDescription objects
one class can return. But this will only marginally reduce the amount of duplication since the SensorDescription is a
majority of the code in the class currently.

Another one would be to add select boxes as additional information for the connection type, the parameter and the unit in the fields section, but this would leave
the table overview less useful for less savy users or require a more complicated process of drawing it in the frontend.
Also need to consider some like parameter/unit (might or might not be) linked together making this less than trivial.  
'''


'''
Every new rule added has to also be added to the sensor_config_serializer.py  validate() method to actually apply.
'''
class IntRangeRuleInclusive(NamedTuple):
    min: int
    max: int

class ValidHttpEndpointRule(NamedTuple):
    regex: str

'''
The type of a field needs to be correctly validated the same as any rules applying to the field!  
'''
class FieldType(Enum):
    INTEGER = 'int'
    STRING = 'str'

class FieldDescription(NamedTuple):
    name: str
    type: FieldType
    rules: List[object]

'''
The connection type is required and shows up as a column in the frontend.
'''
class ConnectionType(Enum):
    PIN = 'Pin'
    HTTP = 'Http'
    FARMBOT = 'Farmbot'

'''
Every sensor class needs to correctly return a full sensor description object on getDescription()
These get drawn in frontend as hardware connection.
'''
class SensorDescription(NamedTuple):
    """
    When creating a sensor class generate a corresponding uuid for example like so using the python console:

    import uuid
    uuid.uuid4()

    !!! NEVER CHANGE OR DELETE THE sensor_class_id, the DB will store them to identify the class !!!
    """
    sensor_class_id: str
    model: str
    connection: ConnectionType
    '''
    The parameter can be translated by the fronted if it is a semicolon (;) separated string with english first german second (only languages that supports currently) 
    '''
    parameter: str
    '''
    The unit gets stored in the dashboard and used in the frontend as is the graph hover.
    '''
    unit: str
    '''
    The tags are meant to add additional information for example a minimum interval   
    '''
    tags: dict[str, str]
    '''
    Fields are inputs by the user and are stored as a json dict in the additionalInformation DB column
    '''
    fields: List[FieldDescription]


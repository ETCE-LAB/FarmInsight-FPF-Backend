from .typed_action_script_factory import TypedActionScriptFactory
from .typed_action_script import ActionScript

"""
ONLY ActionScript classes imported here will be visible to the program and count as supported.
To disable any action scripts just comment out the line by putting a # in front of it
"""

from .tapo_p100_action_script import TapoP100SmartPlugActionScriptWithDelay
from .shelly_plug_s_http_action_script import ShellyPlugHttpActionScript, ShellyPlugMqttActionScript
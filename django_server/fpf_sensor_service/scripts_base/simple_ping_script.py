import json
import requests

from .script_description import ScriptDescription
from .typed_script import TypedScript, ScriptType


class SimplePing(TypedScript):
    @staticmethod
    def get_script_type() -> ScriptType:
        return ScriptType.PING

    def init_additional_information(self):
        pass

    @staticmethod
    def get_description() -> ScriptDescription:
        return ScriptDescription(
            script_class_id='',
            fields=[],
        )

    def run(self, payload=None) -> any:
        response = requests.get(payload, timeout=10)
        return response.status_code == 200

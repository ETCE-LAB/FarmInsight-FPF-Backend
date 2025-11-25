import requests

from .script_description import ScriptDescription
from .typed_script import TypedScript, ScriptType


class HardwarePing(TypedScript):
    http_endpoint = None

    @staticmethod
    def get_script_type() -> ScriptType:
        return ScriptType.PING

    def init_additional_information(self):
        self.http_endpoint = self.model.pingEndpoint

    @staticmethod
    def get_description() -> ScriptDescription:
        return ScriptDescription(
            script_class_id='',
            fields=[],
        )

    def run(self, payload=None) -> any:
        response = requests.get(self.http_endpoint, timeout=10)
        return response.status_code == 200
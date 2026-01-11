import aiohttp

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

    async def run(self, payload=None) -> any:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.http_endpoint, timeout=10) as response:
                return response.status == 200

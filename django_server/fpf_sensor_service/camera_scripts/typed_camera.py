import json
import requests

from fpf_sensor_service.scripts_base import ScriptDescription, TypedScript, ScriptType, FieldDescription, FieldType, ValidHttpEndpointRule


class TypedCamera(TypedScript):
    snapshot_url = None

    def init_additional_information(self):
        additional_information = json.loads(self.model.additionalInformation)
        self.snapshot_url = additional_information['snapshotUrl']

    @staticmethod
    def get_description() -> ScriptDescription:
        return ScriptDescription(
            script_class_id='cacacaca-caca-caca-caca-cacacacacaca',
            fields=[
                FieldDescription(
                    id='snapshotUrl',
                    name='snapshotUrl',
                    description='',
                    type=FieldType.STRING,
                    rules=[
                        ValidHttpEndpointRule(),
                    ]
                ),
            ]
        )

    @staticmethod
    def get_script_type() -> ScriptType:
        return ScriptType.CAMERA

    def run(self, payload=None):
        response = requests.get(self.snapshot_url, stream=True)
        return response.raw

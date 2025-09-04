import requests

from django_server import settings

from fpf_sensor_service.models import Configuration, ConfigurationKeys
from fpf_sensor_service.utils import get_logger


logger = get_logger()


def get_fpf_id() -> str or None:
    fpf_config = Configuration.objects.filter(key=ConfigurationKeys.FPF_ID.value).first()
    if not fpf_config:
        logger.debug('!!! FPF ID CONFIGURATION LOST, UNABLE TO PROCEED !!!')
        return None
    return fpf_config.value


def request_api_key() -> str or None:
    fpf_id = get_fpf_id()
    if fpf_id is None:
        return None

    url = f"{settings.MEASUREMENTS_BASE_URL}/api/fpfs/{fpf_id}/api-key"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error('!!! Request for new API Key failed !!!')
        return None
    else:
        api_key = Configuration.objects.filter(key=ConfigurationKeys.API_KEY.value).first()
        if api_key:
            return api_key.value


def get_or_request_api_key() -> str or None:
    api_key = Configuration.objects.filter(key=ConfigurationKeys.API_KEY.value).first()
    if not api_key:
        return request_api_key()
    return api_key.value
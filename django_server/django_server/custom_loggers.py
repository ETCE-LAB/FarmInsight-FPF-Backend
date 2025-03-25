import logging
import requests
from django.utils import timezone

class APILogHandler(logging.Handler):
    def __init__(self, api_url, fpf_id):
        super().__init__()
        self.api_url = api_url

        # in the case that one would want to also hook up django error messages as well we can also statically provide the fpfId
        # since we don't have access to the model at this stage and django messages don't have the extra info
        self.fpf_id = fpf_id

    '''
    I was hoping to also be able to relay *default* django logs to the dashboard through this, but since it relies on the extra info api_key that's out...
    is there a way to remedy this and retrieve fpfId/apikey here?
    '''
    def emit(self, record):
        log_entry = self.format(record)
        extra_info = getattr(record, 'extra', {})
        if not 'api_key' in extra_info:
            return

        payload = {
            'message': log_entry,
            'level': record.levelname,
            'createdAt': timezone.now().isoformat(),
        }

        if 'fpfId' in extra_info:
            payload['fpfId'] = str(extra_info['fpfId'])
        elif self.fpf_id != '':
            payload['fpfId'] = self.fpf_id

        if 'sensorId' in extra_info:
            payload['sensorId'] = str(extra_info['sensorId'])

        try:
            requests.post(self.api_url, json=payload, headers={
                'Authorization': f'ApiKey {extra_info['api_key']}'
            })
        except requests.RequestException as e:
            self.handleError(record)


class CustomConsoleLogger(logging.StreamHandler):
    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            extra_info = getattr(record, 'extra', {})
            if 'sensorId' in extra_info:
                msg = f'{msg} sensor: {extra_info["sensorId"]}'

            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)
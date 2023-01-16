import json
import time
from logging import Formatter, LogRecord

from . import UniversalJSONEncoder


LOG_RECORD_BUILT_IN_ATTRS = [
    'asctime', 'created', 'exc_info', 'exc_text', 'filename', 'args',
    'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module', 'msg',
    'msecs', 'msecs', 'message', 'name', 'pathname', 'process', 'stack_info',
    'processName', 'relativeCreated', 'thread', 'threadName', 'extra',
    # Also exclude legacy 'props'
    'props',
]


class JsonFormatter(Formatter):

    converter = time.gmtime
    default_time_format = '%Y-%m-%dT%H:%M:%S'
    default_msec_format = '%s.%03d+00:00'

    def format(self, record: LogRecord) -> str:

        result = self._get_main_fields(record)
        if extra := self._get_extra_fields(record):
            result['extra'] = extra

        return json.dumps(result, cls=UniversalJSONEncoder)

    @staticmethod
    def _get_extra_fields(record: LogRecord) -> dict:
        return {
            key: value
            for key, value in record.__dict__.items()
            if key not in LOG_RECORD_BUILT_IN_ATTRS
        }

    def _get_main_fields(self, record: LogRecord) -> dict:
        if record.exc_text:
            traceback = record.exc_text
        elif record.exc_info:
            traceback = self.formatException(record.exc_info)
        else:
            traceback = record.stack_info
        data = {
            'logger_name': record.name,
            'level': record.levelname,
            'timestamp': self.formatTime(record),
            'message': record.getMessage(),
            'pathname': record.pathname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'traceback': traceback,
        }
        return data

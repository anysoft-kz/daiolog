import copy
from logging import LogRecord, Formatter
from logging.handlers import QueueHandler as BuildInQueueHandler
from multiprocessing import Queue
from typing import Any

queue = Queue()
formatter = Formatter()


class QueueHandler(BuildInQueueHandler):
    
    def __init__(self):
        super().__init__(queue)

    def prepare(self, record: LogRecord) -> Any:
        msg = record.getMessage()
        exc_text = formatter.formatException(record.exc_info) if record.exc_info else None
        record = copy.copy(record)
        record.msg = msg
        record.args = None
        record.exc_text = exc_text
        record.exc_info = None
        return record

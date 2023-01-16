from logging import StreamHandler
from logging.handlers import QueueListener as BuildInQueueListener
from .handler import queue
from .formatters import JsonFormatter


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class QueueListener(BuildInQueueListener, metaclass=MetaSingleton):

    def __init__(self, *, stream=None, respect_handler_level=False):
        handler = StreamHandler(stream=stream)
        handler.setFormatter(JsonFormatter())
        handler.setLevel(1)
        super().__init__(queue, handler, respect_handler_level=respect_handler_level)

    def start(self) -> None:
        if self._thread is None:
            super().start()

    def stop(self) -> None:
        if self._thread is not None:
            super().stop()



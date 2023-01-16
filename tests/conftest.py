import logging
import typing as t


import pytest

@pytest.fixture
def list_handler():
    class ListHandler(logging.StreamHandler):
        def __init__(self, level=logging.NOTSET, stream=None):
            self.record_history: list[logging.LogRecord] = []
            super(ListHandler, self).__init__(stream)
            self.setLevel(level)

        def handle(self, record: logging.LogRecord) -> bool:
            self.record_history.append(record)
            return super(ListHandler, self).handle(record)

    return ListHandler


@pytest.fixture
def list_logger_handler(list_handler) -> t.Callable[[t.Union[str, logging.Logger]], list[logging.LogRecord]]:
    """
    Возвращает функцию для установки экземпляра ListHandler для заданного логгера.
    Вызов функции возвращает list в который добавляются LogRecords публикуемые в логгер
    """
    import io

    loggers: list[tuple[logging.Logger, list_handler, t.Any, bool]] = []

    def get_logger(logger: t.Union[str, logging.Logger]):
        if isinstance(logger, str):
            logger = logging.getLogger(logger)
        logger_level = logger.level
        logger.setLevel(1)
        logger_propagate = logger.propagate
        logger.propagate = False
        new_handler = list_handler(logging.DEBUG, io.StringIO())
        new_handler.setLevel(1)
        loggers.append((logger, new_handler, logger_level, logger_propagate))
        logger.addHandler(new_handler)
        return new_handler.record_history

    yield get_logger
    for log, handler, level, propagate in loggers:
        if handler in log.handlers:
            log.handlers.remove(handler)
        log.setLevel(level)
        log.propagate = propagate
import logging
import logging.config
import sys
from threading import Thread

from daiolog import QueueListener, QueueHandler, JsonFormatter
from multiprocessing import Process


def test_success_publish_log_to_queue_listener(mocker):
    records = []

    def mock_emit(rec):
        records.append(rec)

    listener = QueueListener()
    mocker.patch.object(listener.handlers[0], 'emit', mock_emit)

    logger = logging.getLogger('test_success_publish_log_to_queue_listener')
    logger.setLevel(logging.INFO)

    handler = QueueHandler()
    handler.setLevel(logging.DEBUG)
    logger.handlers.append(handler)

    listener.start()
    logger.info('Test info log')
    listener.stop()

    log_record = records.pop()

    assert isinstance(log_record, logging.LogRecord)
    assert log_record.msg == 'Test info log'
    assert log_record.levelname == 'INFO'
    assert log_record.name == 'test_success_publish_log_to_queue_listener'


def test_default_listener_handler():
    listener = QueueListener()
    assert len(listener.handlers) == 1
    handler = listener.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == 1
    assert isinstance(handler.formatter, JsonFormatter)
    assert handler.stream is sys.stderr


def test_custom_stream():
    QueueListener._instances.clear()
    listener = QueueListener(stream=sys.stdout)
    assert listener.handlers[0].stream is sys.stdout


def test_singleton_listener():

    assert QueueListener() is QueueListener()


def test_idempotence_start_listener():
    listener = QueueListener()
    listener.start()
    thread1: Thread = listener._thread
    listener.start()
    thread2 = listener._thread
    listener.stop()
    assert thread1 is thread2
    assert thread1.is_alive() is False


def test_idempotence_stop_listener():
    listener = QueueListener()
    listener.start()
    listener.stop()
    assert listener._thread is None
    listener.stop()


def test_continues_start_listener():
    listener = QueueListener()
    listener.start()
    thread1: Thread = listener._thread
    listener.stop()
    listener.start()
    thread2 = listener._thread
    listener.stop()
    assert thread1 is not thread2


def test_load_dict_logging_config(mocker):

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'default': {
                'level': 'INFO',
                'class': 'daiolog.QueueHandler',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default'],
                'level': 'WARNING',
                'propagate': False
            },
            'test_load_dict_logging_config': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            },
        }
    }

    logging.config.dictConfig(LOGGING_CONFIG)

    records = []

    def mock_emit(rec):
        records.append(rec)

    listener = QueueListener()
    mocker.patch.object(listener.handlers[0], 'emit', mock_emit)

    def main():
        logger = logging.getLogger('test_load_dict_logging_config')
        logger.info('Start main')
        ...
        logger.info('Finish main')

    QueueListener().start()
    main()
    QueueListener().stop()

    assert records[0].msg == 'Start main'
    assert records[1].msg == 'Finish main'



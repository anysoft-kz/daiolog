import sys
import logging
import os
import threading

from daiolog import QueueHandler


def test_handlers_use_one_instance_of_queue():
    handler1 = QueueHandler()
    handler2 = QueueHandler()
    assert handler1.queue is handler2.queue


def test_handled_log_record_attributes():
    logger = logging.getLogger('test_handled_log_record_attributes')
    handler = QueueHandler()
    logger.handlers.append(handler)
    try:
        1 / 0
    except:
        logger.exception('test ZeroDivision %s %s', 'test-arg1', 'test-arg2',
                         stack_info=True, extra={'extra1': 123, 'extra2': True})

    rec = handler.queue.get()

    assert isinstance(rec, logging.LogRecord)
    assert rec.name == 'test_handled_log_record_attributes'
    assert rec.msg == 'test ZeroDivision test-arg1 test-arg2'
    assert rec.args is None
    assert hasattr(rec, 'message') is False
    assert rec.levelname == 'ERROR'
    assert rec.levelno == 40
    assert rec.pathname == __file__
    assert rec.filename == 'test_handler.py'
    assert rec.module == 'test_handler'
    assert rec.exc_info is None
    if sys.version_info > (3, 11):
        assert rec.lineno == 22
        assert rec.exc_text == (
            'Traceback (most recent call last):\n'
            '  File '
            f'"{__file__}", '
            'line 20, in test_handled_log_record_attributes\n'
            '    1 / 0\n'
            '    ~~^~~\n'
            'ZeroDivisionError: division by zero'
        )
    else:
        assert rec.lineno == 22
        assert rec.exc_text == (
            'Traceback (most recent call last):\n'
            '  File '
            f'"{__file__}", '
            'line 20, in test_handled_log_record_attributes\n'
            '    1 / 0\n'
            'ZeroDivisionError: division by zero'
        )
    assert rec.stack_info.find("logger.exception('test ZeroDivision %s %s', 'test-arg1', 'test-arg2'") > 0
    assert rec.funcName == 'test_handled_log_record_attributes'
    assert isinstance(rec.created, float)
    assert isinstance(rec.msecs, float)
    assert rec.thread == threading.get_ident()
    assert rec.threadName == threading.current_thread().name
    assert rec.processName == 'MainProcess'
    assert rec.process == os.getpid()
    assert getattr(rec, 'extra1') == 123
    assert getattr(rec, 'extra2') is True

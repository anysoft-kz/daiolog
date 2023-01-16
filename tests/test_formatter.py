import json
import logging
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import pytest

from daiolog import JsonFormatter


def test_formatter_return_json_serialize_string(list_logger_handler):
    logger = logging.getLogger('test_formatter_return_json_serialize_string')
    log_records = list_logger_handler(logger)

    logger.info('test message %s', 'test-arg')

    formatter = JsonFormatter()

    record = log_records.pop()
    result = formatter.format(record)
    record_time = dt.datetime.fromtimestamp(
        record.created, tz=dt.timezone.utc
    ).isoformat(timespec='milliseconds')
    assert json.loads(result) == {
        'logger_name': record.name,
        'level': 'INFO',
        'timestamp': record_time,
        'message': 'test message test-arg',
        'pathname': record.pathname,
        'module': 'test_formatter',
        'function': 'test_formatter_return_json_serialize_string',
        'line': record.lineno,
        'traceback': None,
    }


@dataclass
class TestValueObject:
    attr: int


@pytest.mark.parametrize('value, result', (
        (123, 123),
        (123.456, 123.456),
        ('Test string', 'Test string'),
        (None, None),
        (True, True),
        (False, False),
        ([1, 2, 3], [1, 2, 3]),
        ((1, 2, 3), [1, 2, 3]),
        ({1, 2, 3}, [1, 2, 3]),
        (dt.date(2023, 1, 1), '2023-01-01'),
        (dt.datetime(2023, 1, 1, 1, 2, 3), '2023-01-01T01:02:03'),
        (dt.datetime(2023, 1, 1, 1, 2, 3, tzinfo=dt.timezone.utc), '2023-01-01T01:02:03+00:00'),
        ({1: '1', 2: '2'}, {'1': '1', '2': '2'}),
        (Decimal(123).quantize(Decimal('0.00')), "Decimal('123.00')"),
        (UUID(int=1), "UUID('00000000-0000-0000-0000-000000000001')"),
        (TestValueObject(1), 'TestValueObject(attr=1)'),
        (b'abc', "b'abc'"),
))
def test_extra_arguments_serialize(value, result, list_logger_handler):

    logger = logging.getLogger('test_extra_arguments_serialize')
    log_records = list_logger_handler(logger)
    formatter = JsonFormatter()
    logger.info('test message %s', 'test-arg', extra={
        'key': value
    })

    record = log_records.pop()
    res = json.loads(formatter.format(record))['extra']

    assert res['key'] == result


#  dict


def test_exc_info_serialize(list_logger_handler):
    logger = logging.getLogger('test_exc_info_serialize')
    log_records = list_logger_handler(logger)
    formatter = JsonFormatter()

    try:
        1 / 0
    except:
        logger.exception('test_exception')

    record = log_records.pop()
    result = json.loads(formatter.format(record))

    assert result['traceback'] == (
        'Traceback (most recent call last):\n'
        '  File '
        f'"{record.pathname}", '
        f'line {record.lineno - 2}, in {record.funcName}\n'
        '    1 / 0\n'
        'ZeroDivisionError: division by zero'
    )


def test_stack_info_serialize(list_logger_handler):
    logger = logging.getLogger('test_stack_info_serialize')
    log_records = list_logger_handler(logger)
    formatter = JsonFormatter()

    logger.info('test stack info', stack_info=True)
    record = log_records.pop()
    result: str = json.loads(formatter.format(record))['traceback']

    assert result.startswith('Stack (most recent call last):\n')
    assert result == record.stack_info


def test_not_standard_logging_level_serialize(list_logger_handler):
    logger = logging.getLogger('test_not_standard_logging_level_serialize')
    logger.setLevel(0)
    log_records = list_logger_handler(logger)
    formatter = JsonFormatter()

    logger.log(1, 'test stack info', stack_info=True)
    record = log_records.pop()
    result: str = json.loads(formatter.format(record))['level']

    assert result == 'Level 1'

    logger.log(99, 'test stack info', stack_info=True)
    record = log_records.pop()
    result: str = json.loads(formatter.format(record))['level']
    assert result == 'Level 99'


def test_exc_info_priority_stack_info_serialize(list_logger_handler):
    logger = logging.getLogger('test_exc_info_priority_stack_info_serialize')
    log_records = list_logger_handler(logger)
    formatter = JsonFormatter()

    try:
        1 / 0
    except Exception as err:
        logger.exception('test_exception', exc_info=err, stack_info=True)

    record = log_records.pop()
    result = json.loads(formatter.format(record))

    assert record.exc_text is not None
    assert record.stack_info is not None
    assert record.exc_text != record.stack_info
    assert result['traceback'] == record.exc_text

import logging
import pathlib

import pytest

import daiolog
from daiolog import QueueListener
from os import path


def get_config_file_name():
    return str(path.join(pathlib.Path(__file__).parent, 'log_config.conf'))


class TestEntryPoint:

    def test_dict_config(self, mocker):
        records = []

        def mock_emit(rec):
            records.append(rec)

        listener = QueueListener()
        mocker.patch.object(listener.handlers[0], 'emit', mock_emit)

        LOG_CONFIG = {
            'version': 1,
            'disable_existing_loggers': True,
            'handlers': {
                'default': {
                    'level': 'INFO',
                    'class': 'daiolog.QueueHandler',
                },
            },
            'loggers': {
                # '': {  # root logger
                #     'handlers': ['default'],
                #     'level': 'WARNING',
                #     'propagate': False
                # },
                'test_dict_config': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': True
                },
            }
        }

        @daiolog.entrypoint(LOG_CONFIG)
        def main():
            logger = logging.getLogger('test_dict_config')
            logger.info('Test info')
            logger.debug('Test debug')

        main()

        assert listener._thread is None
        assert len(records) == 1
        log_rec = records[0]
        assert isinstance(log_rec, logging.LogRecord)
        assert log_rec.msg == 'Test info'
        assert log_rec.levelname == 'INFO'
        assert log_rec.name == 'test_dict_config'

    def test_file_config(self, mocker):
        records = []

        def mock_emit(rec):
            records.append(rec)

        listener = QueueListener()
        mocker.patch.object(listener.handlers[0], 'emit', mock_emit)

        config_file_name = get_config_file_name()

        @daiolog.entrypoint(config_file_name)
        def main():
            logger = logging.getLogger('test_file_config')
            logger.info('Test info')
            logger.debug('Test debug')

        main()

        assert listener._thread is None
        assert len(records) == 1
        log_rec = records[0]
        assert isinstance(log_rec, logging.LogRecord)
        assert log_rec.msg == 'Test info'
        assert log_rec.levelname == 'INFO'
        assert log_rec.name == 'test_file_config'

    def test_function_config(self, mocker):
        records = []

        def mock_emit(rec):
            records.append(rec)

        listener = QueueListener()
        mocker.patch.object(listener.handlers[0], 'emit', mock_emit)

        def log_config():
            return {
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
                    'test_function_config': {
                        'handlers': ['default'],
                        'level': 'INFO',
                        'propagate': False
                    },
                }
            }

        @daiolog.entrypoint(log_config)
        def main():
            logger = logging.getLogger('test_function_config')
            logger.info('Test info')
            logger.debug('Test debug')

        main()

        assert listener._thread is None
        assert len(records) == 1
        log_rec = records[0]
        assert isinstance(log_rec, logging.LogRecord)
        assert log_rec.msg == 'Test info'
        assert log_rec.levelname == 'INFO'
        assert log_rec.name == 'test_function_config'

    def test_method_decorate(self, mocker):
        records = []

        def mock_emit(rec):
            records.append(rec)

        listener = QueueListener()
        mocker.patch.object(listener.handlers[0], 'emit', mock_emit)

        LOG_CONFIG = {
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
                'test_method_decorate': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': False
                },
            }
        }

        class Test:

            def __init__(self, value):
                self._value = value

            @daiolog.entrypoint(LOG_CONFIG)
            def main(self):
                logger = logging.getLogger('test_method_decorate')
                logger.info('Test info %s', self._value)
                logger.debug('Test debug %s', self._value)

        Test('value1').main()
        assert listener._thread is None
        assert len(records) == 1
        log_rec = records[0]
        assert isinstance(log_rec, logging.LogRecord)
        assert log_rec.msg == 'Test info value1'
        assert log_rec.levelname == 'INFO'
        assert log_rec.name == 'test_method_decorate'

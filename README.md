# Do asyncio logging

JSON logging in a separate thread for asyncio projects

## Basic Usage

```python
import os
import logging
import logging.config
from daiolog import QueueListener

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
        'my.packg': { 
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    } 
}

logging.config.dictConfig(LOGGING_CONFIG)


def main():
    logger = logging.getLogger('my.packg')
    logger.info('Start main', extra={'pid': os.getpid()})
    ...
    logger.info('Finish main', extra={'pid': os.getpid()})

if __name__ == '__main__':
    QueueListener().start()
    main()
    QueueListener().stop()


# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.511+00:00", "message": "Start main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 35, "traceback": null, "extra": {"pid": 60720}}
# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.512+00:00", "message": "Finish main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 37, "traceback": null, "extra": {"pid": 60720}}
```


## Usage with decorator

**With dict config**
```python
import os
import logging
import logging.config
import daiolog 

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
        'my.packg': { 
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    } 
}

@daiolog.entrypoint(LOGGING_CONFIG)
def main():
    logger = logging.getLogger('my.packg')
    logger.info('Start main', extra={'pid': os.getpid()})
    ...
    logger.info('Finish main', extra={'pid': os.getpid()})

if __name__ == '__main__':
    main()


# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.511+00:00", "message": "Start main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 35, "traceback": null, "extra": {"pid": 60720}}
# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.512+00:00", "message": "Finish main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 37, "traceback": null, "extra": {"pid": 60720}}
```


**With file config**
```python
import os
import logging
import logging.config
import daiolog 

@daiolog.entrypoint('./logging.conf')
def main():
    logger = logging.getLogger('my.packg')
    logger.info('Start main', extra={'pid': os.getpid()})
    ...
    logger.info('Finish main', extra={'pid': os.getpid()})

if __name__ == '__main__':
    main()


# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.511+00:00", "message": "Start main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 35, "traceback": null, "extra": {"pid": 60720}}
# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.512+00:00", "message": "Finish main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 37, "traceback": null, "extra": {"pid": 60720}}
```


**With function**
```python
import os
import logging
import logging.config
import daiolog 

def get_logging_config():
    return os.environ.get('LOGGING_FILE_CONFIG', './logging.conf')

@daiolog.entrypoint(get_logging_config)
def main():
    logger = logging.getLogger('my.packg')
    logger.info('Start main', extra={'pid': os.getpid()})
    ...
    logger.info('Finish main', extra={'pid': os.getpid()})

if __name__ == '__main__':
    main()


# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.511+00:00", "message": "Start main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 35, "traceback": null, "extra": {"pid": 60720}}
# {"logger_name": "my.packg", "level": "INFO", "timestamp": "2023-01-16T09:21:43.512+00:00", "message": "Finish main", "pathname": "__main__.py", "module": "__main__", "function": "main", "line": 37, "traceback": null, "extra": {"pid": 60720}}
```


Release Notes

1.1.0
- Add entrypoint function decorator(`daiolog.entrypoint`) for config logging and start/stop `QueueListener`
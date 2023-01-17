import functools
import logging.config
import typing as t

from daiolog import QueueListener

__all__ = ['entrypoint']


class EntrypointDecorator:

    def __init__(self, config: t.Union[str, dict, t.Callable[..., t.Union[str, dict]]]):
        self._config = config

    def __call__(self, func: t.Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            listener = QueueListener()
            self._load_logging_config()
            try:
                listener.start()
                return func(*args, **kwargs)
            finally:
                listener.stop()

        return wrapper

    def _load_logging_config(self, config=None):
        if config is None:
            config = self._config
        if isinstance(config, t.Callable):
            self._load_logging_config(config=config())
        elif isinstance(config, dict):
            logging.config.dictConfig(config)
        elif isinstance(config, str):
            logging.config.fileConfig(config, disable_existing_loggers=True)


entrypoint = EntrypointDecorator

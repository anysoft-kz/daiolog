import json
import typing
import warnings
import datetime as dt


class UniversalJSONEncoder(json.JSONEncoder):
    _encoders = {
        dt.date: lambda x: x.isoformat(),
        dt.datetime: lambda x: x.isoformat(),
        set: list
    }

    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            pass

        if type(obj) in UniversalJSONEncoder._encoders:
            try:
                return UniversalJSONEncoder._encoders[type(obj)](obj)
            except:  # noqa
                warnings.warn("Encoding function %s used for type %s raised an exception. Trying something else." % \
                              (UniversalJSONEncoder._encoders[type(obj)].__name__, type(obj)))
        return repr(obj)

    @classmethod
    def register_converter(cls, type: typing.Type, converter):  # noqa
        cls._encoders[type] = converter

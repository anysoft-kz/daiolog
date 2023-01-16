import json
from uuid import UUID

from daiolog import UniversalJSONEncoder


def test_register_converter():
    data = {'uuid': UUID(int=1)}
    assert json.dumps(data, cls=UniversalJSONEncoder) == '{"uuid": "UUID(\'00000000-0000-0000-0000-000000000001\')"}'
    UniversalJSONEncoder.register_converter(UUID, str)
    assert json.dumps(data, cls=UniversalJSONEncoder) == '{"uuid": "00000000-0000-0000-0000-000000000001"}'

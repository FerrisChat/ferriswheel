from typing import Any

import json

__all__ = ('to_json', 'from_json')

try:
    import orjson
    HAVE_ORJSON = True
except ImportError:
    HAVE_ORJSON = False


if HAVE_ORJSON:
    def to_json(self, obj: Any) -> str:
        return orjson.dumps(obj).decode('utf-8')
    
    from_json = orjson.loads
else:
    def to_json(self, obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=True)
    
    from_json = json.loads
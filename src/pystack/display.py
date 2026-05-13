import json


def format_value(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float, complex)):
        return str(value)
    return repr(value)


def format_stack(items):
    return "\n".join(format_value(v) for v in items)

import json


def format_value(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float, complex)):
        return str(value)
    return repr(value)


MAX_VISIBLE = 5


def format_stack(items):
    if len(items) > MAX_VISIBLE:
        visible = items[-MAX_VISIBLE:]
        return "\n".join(["..."] + [format_value(v) for v in visible])
    return "\n".join(format_value(v) for v in items)

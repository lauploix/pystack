from pystack.display import format_stack, format_value


def test_format_empty_stack_is_empty_string():
    assert format_stack([]) == ""


def test_format_int():
    assert format_value(3) == "3"


def test_format_float():
    assert format_value(2.5) == "2.5"


def test_format_string_uses_double_quotes():
    assert format_value("a") == '"a"'


def test_format_string_with_space():
    assert format_value("a b") == '"a b"'


def test_format_string_escapes_embedded_quote():
    # json.dumps semantics: embedded double quotes are escaped.
    assert format_value('say "hi"') == '"say \\"hi\\""'


def test_format_stack_one_per_line_bottom_first():
    # Bottom of stack first, top last.
    assert format_stack([3, "a1"]) == '3\n"a1"'


def test_format_stack_matches_example_sequence():
    # Mirrors the example: 3, "a", 1 displayed bottom-to-top.
    assert format_stack([3, "a", 1]) == '3\n"a"\n1'

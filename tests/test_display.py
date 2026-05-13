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


def test_format_stack_shows_all_when_exactly_five():
    assert format_stack([1, 2, 3, 4, 5]) == "1\n2\n3\n4\n5"


def test_format_stack_truncates_when_more_than_five():
    # 7 items: show "..." and the 5 most recent (top of stack).
    assert format_stack([1, 2, 3, 4, 5, 6, 7]) == "...\n3\n4\n5\n6\n7"


def test_format_stack_truncation_keeps_top_at_bottom():
    items = list(range(10))  # 0..9, top is 9
    out = format_stack(items)
    lines = out.splitlines()
    assert lines[0] == "..."
    assert lines[-1] == "9"
    assert len(lines) == 6  # "..." + 5 items

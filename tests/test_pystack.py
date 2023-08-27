from pystack import pystack

def test_int_add():
    s = pystack(["'abc'", "1", "3", "+"])
    assert s == ["abc", 4]

def test_int_minus():
    s = pystack(["'abc'", "1", "3", "-"])
    print (s)
    assert s == ["abc", -2]


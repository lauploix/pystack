import ast
from collections import deque

import numpy as np

UNDO_MAX = 1024

# Inspired by http://www.quickclose.com.au/tut2.htm


class StackException(Exception):
    def __init__(self, msg="Unknown Exception", inner=None):
        self.msg = msg
        self.inner = inner
        super().__init__(msg)


class RpnStack:
    def __init__(self, tokens=None, raises=False, slots=None, undo=None):
        self.__stack = []
        self.raises = raises
        if tokens:
            self.__stack.extend(tokens)
        self.slots = slots if slots is not None else {}
        self.undo = undo if undo is not None else deque(maxlen=UNDO_MAX)
        self.exec_map = {
            "+": self._exec_plus,
            "-": self._exec_minus,
            "*": self._exec_mult,
            "**": self._exec_power,
            "/": self._exec_div,
            "//": self._exec_floordiv,
            "%": self._exec_mod,
        }
        # From numpy, list fucntions (numpy.ufunc),
        # find the ones that are not deprecated
        # and add them to the exec_map togther with their
        # argument number

    @property
    def msg(self):
        return self.exception and self.exception.msg or ""

    def __len__(self):
        return len(self.__stack)

    def size(self):
        return len(self.__stack)

    def pop(self):
        return self.__stack.pop()

    def top(self):
        return self.__stack[-1]

    def push(self, value):
        self.__stack.append(value)

    # Tries to turn the last element into an operation
    # If the operation is not found, it is pushed back onto the stack
    # and raise an error
    # if the operation is found, it is executed
    # If the operation is a literal, it is pushed onto the stack
    def exec(self, token=None, tokens=None):
        # TODO: fix this algorithm to take into account the strings
        # with spaces in them
        self.exception = None

        if tokens is not None:
            for token in tokens:
                # Try to execute the token, one by one.
                # There is no transaction
                self.exec(token=token)
        else:
            f = None  # tell if we have found the operation
            try:
                # self.pop() will execute the last element of the stack
                # as if its string was entered as a command
                # Is this what I want?
                token = token or self.pop()

                # Snapshot the current stack for `undo`, except when
                # the operation itself is `undo` (which would be a
                # self-recording loop).
                if token.lower() != "undo":
                    self.undo.append(list(self.__stack))

                # First we check is there is a registered function
                # or an _exec_ function
                f = self.exec_map.get(token.lower()) or getattr(
                    self, f"_exec_{token.lower()}", None
                )
                if not f:
                    # If not, we try to find a numpy function
                    f = getattr(np, token.lower(), None)
                    if f and type(f) is not np.ufunc:
                        # We only wants the functions,
                        # not the constants or classes
                        f = None
                # If we found a function, we execute it
                if f and type(f) is np.ufunc:
                    # Nb of arguments it takes
                    n_args = f.nin
                    args = self.__pop_as_list(n_args)
                    self.push(f(*args))
                elif f:
                    f()
                else:
                    # Otherwise we try to evaluate the token as a
                    # python literal
                    # Therefore must be a string, a number, a list,
                    # a tuple, a dict...
                    value = ast.literal_eval(token)
                    self.__stack.append(value)
            except IndexError as e:
                self.exception = StackException(
                    f"Index error with operation {token}: {e}"
                )
            except SyntaxError as e:
                self.exception = StackException(
                    f"Syntax Error: {token}", inner=e
                )
            except ValueError as e:
                if not f:
                    # Unknown token: not a registered op and not a
                    # valid Python literal. Strings must be quoted.
                    self.exception = StackException(
                        f"Operation not found: {token}", inner=e
                    )
                else:
                    self.exception = StackException(
                        f"Error while executing: {token}", inner=e
                    )

            except Exception as e:
                self.exception = StackException(str(e), inner=e)
            finally:
                if self.exception and self.raises:
                    raise self.exception from self.exception.inner

    def __pop_as_list(self, n):
        if len(self) >= n:
            return [self.__stack.pop() for _ in range(n)][::-1]
        raise StackException()

    # execute the swap operation
    def _exec_swap(self):
        a, b = self.__pop_as_list(2)
        self.push(b)
        self.push(a)

    def _exec_e(self):
        self.push(np.e)

    def _exec_pi(self):
        self.push(np.pi)

    def _exec_i(self):
        self.push(1j)

    # execute the size operation
    def _exec_size(self):
        self.push(self.size())

    # evaluate the string in python
    def _exec_eval(self):
        self.push(eval(self.pop()))

    # execute the plus operation
    def _exec_plus(self):
        a, b = self.__pop_as_list(2)
        self.push(a + b)

    # execute the mult operation
    def _exec_mult(self):
        a, b = self.__pop_as_list(2)
        self.push(a * b)

    # execute the mult operation
    def _exec_power(self):
        a, b = self.__pop_as_list(2)
        self.push(a**b)

    # execute the div operation
    def _exec_div(self):
        a, b = self.__pop_as_list(2)
        self.push(a / b)

    # execute the floordiv operation
    def _exec_floordiv(self):
        a, b = self.__pop_as_list(2)
        self.push(a // b)

    # execute the percent operation
    def _exec_mod(self):
        a, b = self.__pop_as_list(2)
        self.push(a % b)

    # execute the minus operation
    def _exec_minus(self):
        a, b = self.__pop_as_list(2)
        self.push(a - b)

    # execute the pick
    def _exec_pick(self):
        self.push(self.__stack[-self.pop()])

    # execute the depth
    def _exec_depth(self):
        self.push(len(self.__stack))

    # execute the clear
    def _exec_clear(self):
        self.__stack = []

    # restore the stack to its state before the previous non-undo op
    def _exec_undo(self):
        if not self.undo:
            raise ValueError("undo: nothing to undo")
        self.__stack = self.undo.pop()

    # execute the dup
    def _exec_dup(self):
        self.push(self.__stack[-1])

    # execute the dup2
    def _exec_dup2(self):
        self.__stack.extend(self.__stack[-2:])

    # execute the dupn
    def _exec_dupn(self):
        self.__stack.extend(self.__stack[-self.pop() :])

    # execute the over
    def _exec_over(self):
        self.push(self.__stack[-2])

    # execute the drop operation
    def _exec_drop(self):
        self.__stack.pop()

    # execute the array operation, transformaing the data into numpy ndarray
    def _exec_array(self):
        # case; entry is a list or tuple
        values = self.__stack.pop()
        out = np.array(values)
        # shape = (len(values), 1)
        self.push(out)

    # pop n, then pop n items and push them as a list (in stack order)
    def _exec_tolist(self):
        n = self.pop()
        self.push(self.__pop_as_list(n))

    # pop top, push Python's len() of it
    def _exec_len(self):
        self.push(len(self.pop()))

    # execute the drop2
    def _exec_drop2(self):
        self.__stack = self.__stack[:-2]

    # execute the drpn
    def _exec_drpn(self):
        n = self.pop()
        self.__stack = self.__stack[:-n]

    # execute the rot (== 3 roll)
    def _exec_rot(self):
        self.__stack[-3:] = self.__stack[-2:] + [
            self.__stack[-3],
        ]

    # execute the roll
    def _exec_roll(self):
        n = self.pop()
        self.__stack[-n:] = self.__stack[-(n - 1) :] + [
            self.__stack[-n],
        ]

    # execute the rolld
    def _exec_rolld(self):
        n = self.pop()
        self.__stack[-n:] = [self.__stack[-1]] + self.__stack[-n:-1]

    # convert top of stack to str
    def _exec_str(self):
        self.push(str(self.pop()))

    # convert top of stack to int
    def _exec_int(self):
        self.push(int(self.pop()))

    # convert top of stack to float
    def _exec_float(self):
        self.push(float(self.pop()))

    # store: pop name (string), pop value, slots[name] = value
    def _exec_sto(self):
        name = self.pop()
        value = self.pop()
        if not isinstance(name, str):
            self.push(value)
            self.push(name)
            raise ValueError(
                f"sto: slot name must be a string, got "
                f"{type(name).__name__}"
            )
        self.slots[name] = value

    # recall: pop name (string), push slots[name]
    def _exec_rcl(self):
        name = self.pop()
        if not isinstance(name, str):
            self.push(name)
            raise ValueError(
                f"rcl: slot name must be a string, got "
                f"{type(name).__name__}"
            )
        if name not in self.slots:
            self.push(name)
            raise KeyError(f"rcl: no such slot {name!r}")
        self.push(self.slots[name])

    # purge: pop name (string), delete slots[name]
    def _exec_purge(self):
        name = self.pop()
        if not isinstance(name, str):
            self.push(name)
            raise ValueError(
                f"purge: slot name must be a string, got "
                f"{type(name).__name__}"
            )
        if name not in self.slots:
            self.push(name)
            raise KeyError(f"purge: no such slot {name!r}")
        del self.slots[name]

    # dups the content of the stack, element by element
    def __iter__(self):
        return iter(self.__stack)


def entries(entry_string):
    for entry in entry_string.strip().split(" "):
        yield entry


if __name__ == "__main__":
    s = RpnStack(raises=True)

    def input_provider():
        while True:
            yield input()

    print(list(s))
    for i in input_provider():
        try:
            s.exec(i)
        except StackException as e:
            print(e.msg)
        print(list(s))

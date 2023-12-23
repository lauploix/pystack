import ast

# Inspired by http://www.quickclose.com.au/tut2.htm


class StackException(Exception):
    pass


def token_finder(token_str):
    SQ, DQ = "'", '"'
    quote = None
    current_token = ""
    for token in token_str.split(" "):
        if quote is None:
            if token[0] in (SQ, DQ):
                if token[-1] == token[0] and len(token) > 1:
                    yield token
                else:
                    quote = token[0]
                    current_token = token
            else:
                yield token
        else:
            current_token += " " + token
            if quote and token.endswith(quote):
                quote = None
                yield current_token
    if quote:
        raise StackException("Unclosed string")


class RpnStack:
    def __init__(self, iterable=None):
        self.__stack = []
        if iterable:
            self.__stack.extend(iterable)
        self.exec_map = {
            "size": self._exec_size,
            "+": self._exec_plus,
            "-": self._exec_minus,
            "*": self._exec_mult,
            "**": self._exec_power,
            "/": self._exec_div,
            "//": self._exec_divdiv,
            "%": self._exec_percent,
            "swap": self._exec_swap,
            "pick": self._exec_pick,
            "drop": self._exec_drop,
            "drop2": self._exec_drop2,
            "drpn": self._exec_drpn,
            "dup": self._exec_dup,
            "dup2": self._exec_dup2,
            "dupn": self._exec_dupn,
            "over": self._exec_over,
            "rot": self._exec_rot,
            "roll": self._exec_roll,
            "rolld": self._exec_rolld,
            "clear": self._exec_clear,
            "depth": self._exec_depth,
        }
        self.msg = ""

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
    def exec(self, tokens_string=None, token=None, tokens=None):
        # TODO: fix this algorithm to take into account the strings
        # with spaces in them
        self.msg = ""

        if tokens_string is not None:
            if tokens_string == "":
                return
            try:
                tokens = list(token_finder(tokens_string))
            except StackException as e:
                self.msg = str(e)
                return

        if tokens is not None:
            for token in tokens:
                self.exec(token=token)
            return

        token = token or self.pop()

        f_name = self.exec_map.get(token.lower())
        if f_name:
            if type(f_name) is str:
                getattr(self, f_name)()
            else:
                f_name()
        else:
            try:
                value = ast.literal_eval(token)
                self.__stack.append(value)
            except SyntaxError:
                self.msg = "Syntax Error: " + token
                return
            except ValueError:
                self.msg = "Operation not found: " + token

    def __pop_as_list(self, n):
        if len(self) >= n:
            return [self.__stack.pop() for _ in range(n)][::-1]
        raise StackException()

    # execute the swap operation
    def _exec_swap(self):
        (a, b) = self.__pop_as_list(2)
        self.push(b)
        self.push(a)

    # execute the size operation
    def _exec_size(self):
        self.push(self.size())

    # execute the plus operation
    def _exec_plus(self):
        (a, b) = self.__pop_as_list(2)
        self.push(a + b)

    # execute the mult operation
    def _exec_mult(self):
        (a, b) = self.__pop_as_list(2)
        self.push(a * b)

    # execute the mult operation
    def _exec_power(self):
        (a, b) = self.__pop_as_list(2)
        self.push(a**b)

    # execute the div operation
    def _exec_div(self):
        (a, b) = self.__pop_as_list(2)
        self.push(a / b)

    # execute the divdiv operation
    def _exec_divdiv(self):
        (a, b) = self.__pop_as_list(2)
        self.push(a // b)

    # execute the percent operation
    def _exec_percent(self):
        (a, b) = self.__pop_as_list(2)
        self.push(a % b)

    # execute the minus operation
    def _exec_minus(self):
        (a, b) = self.__pop_as_list(2)
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

    # execute the dup
    def _exec_dup(self):
        self.push(self.__stack[-1])

    # execute the dup2
    def _exec_dup2(self):
        self.__stack.extend(self.__stack[-2:])

    # execute the dupn
    def _exec_dupn(self):
        n = self.pop()
        self.__stack.extend(self.__stack[-n:])

    # execute the over
    def _exec_over(self):
        self.push(self.__stack[-2])

    # execute the drop operation
    def _exec_drop(self):
        self.__stack.pop()

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

    # dups the content of the stack, element by element
    def __iter__(self):
        return iter(self.__stack)


def entries(entry_string):
    for entry in entry_string.strip().split(" "):
        yield entry


if __name__ == "__main__":
    s = RpnStack()

    def input_provider():
        while True:
            yield input()

    print(list(s))
    for i in input_provider():
        s.exec(i)
        if s.msg:
            print(s.msg)
        print(list(s))

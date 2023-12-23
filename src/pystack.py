import ast

# Inspired by http://www.quickclose.com.au/tut2.htm


class StackException(Exception):
    pass


class RpnStack:
    def __init__(self, iterable=None):
        self.__stack = []
        if iterable:
            self.__stack.extend(iterable)
        self.exec_map = {
            "size": "_exec_size",
            "+": "_exec_plus",
            "-": "_exec_minus",
            "*": "_exec_mult",
            "/": "_exec_div",
            "//": "_exec_divdiv",
            "%": "_exec_percent",
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
            tokens = tokens_string.split(" ")

        if tokens is not None:
            for token in tokens:
                self.exec(token=token)
            return

        token = token or self.pop()

        f_name = self.exec_map.get(token.lower())
        if f_name:
            getattr(self, f_name)()
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

    # dups the content of the stack, element by element
    def __iter__(self):
        return iter(self.__stack)


def entries(entry_string):
    for entry in entry_string.strip().split(" "):
        yield entry


def pystack(input_provider):
    """ROLL
    Moves a specified level to level 1
    ( e.g. 4 ROLL will move level 4 to level 1 )
    ROLLD
    Moves level 1 to a specified level
    ( e.g. 7 ROLLD will move level 1 to level 7 )
    DEPTH
    Counts the number of active levels in the stack placing
    the number on level 1
    DUPN
    Copies a specified number of levels again
    (e.g. 6 DUPN will copy the first six levels of the
    stack again)"""

    stack = []
    print(stack)
    for input_string in input_provider:
        for entry in entries(input_string):
            if entry == "+":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous + last)
            elif entry == "-":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous - last)
            elif entry == "*":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous * last)
            elif entry == "/":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous / last)
            elif entry == "%":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous % last)
            elif entry == "**":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous**last)
            elif entry == "//":
                last = stack.pop()
                previous = stack.pop()
                stack.append(previous // last)
            elif entry.lower() == "swap":
                stack[-2:] = stack[-2:][::-1]
            elif entry.lower() == "dup":
                stack.append(stack[-1])
            elif entry.lower() == "dup2":
                stack.extend(stack[-2:])
            elif entry.lower() == "over":
                stack.append(stack[-2])
            elif entry.lower() == "drop":
                stack.pop()
            elif entry.lower() == "drop2":
                stack.pop()
                stack.pop()
            elif entry.lower() == "drpn":
                for _ in range(stack.pop()):
                    stack.pop()
            elif entry.lower() == "rot":
                stack[-3:] = stack[-2:] + [
                    stack[-3],
                ]
            elif entry.lower() == "pick":
                stack.append(stack[-stack.pop()])
            else:
                try:
                    value = ast.literal_eval(entry)
                    stack.append(value)
                except ValueError:
                    print(">> Value Error")
                except SyntaxError:
                    print(">> Syntax Error")
        print(stack)
    return stack


if __name__ == "__main__":

    def input_provider():
        while True:
            yield input()

    pystack(input_provider())

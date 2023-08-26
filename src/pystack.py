import ast

## Inspired by http://www.quickclose.com.au/tut2.htm 

def entries(entry_string):
    for entry in entry_string.strip().split(" "): yield entry

def pystack():
    """ROLL
Moves a specified level to level 1
( e.g. 4 ROLL will move level 4 to level 1 )
ROLLD
Moves level 1 to a specified level
( e.g. 7 ROLLD will move level 1 to level 7 )
DEPTH
Counts the number of active levels in the stack placing the number on level 1
DUPN
Copies a specified number of levels again
(e.g. 6 DUPN will copy the first six levels of the stack again)
"""


    stack = []
    while (True):
        print (stack)
        value = None
        for entry in entries(input()):
            if entry == "+":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous+last)
            elif entry == "-":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous-last)
            elif entry == "*":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous*last)
            elif entry == "/":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous/last)
            elif entry == "%":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous%last)
            elif entry == "**":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous**last)
            elif entry == "//":
                last = stack.pop()
                previous = stack.pop()
                stack.append (previous//last)
            elif entry.lower() == "swap":
                stack[-2:] = stack [-2:][::-1]
            elif entry.lower() == "dup":
                stack.append (stack [-1])
            elif entry.lower() == "dup2":
                stack.extend (stack [-2:])
            elif entry.lower() == "over":
                stack.append (stack [-2])
            elif entry.lower() == "drop":
                stack.pop()
            elif entry.lower() == "drop2":
                stack.pop()
                stack.pop()
            elif entry.lower() == "drpn":
                for _ in range(stack.pop()):
                    stack.pop()
            elif entry.lower() == "rot":
                stack[-3:]=stack[-2:] + [stack[-3],]  
            elif entry.lower() == "pick":
                stack.append(stack[-stack.pop()])
            else:
                try:
                    value = ast.literal_eval(entry)
                    stack.append(value)
                except ValueError:
                    print (">> Value Error")
                except SyntaxError:
                    print (">> Syntax Error")


if __name__ == "__main__":
    pystack()
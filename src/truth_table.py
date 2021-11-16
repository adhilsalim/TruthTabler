import itertools
import re
from prettytable import PrettyTable
from exceptions import BracketException, InvalidExpressionException


def getVariables(expr: list):
    # Variables have to be a letter and of length 1
    return sorted({x for x in expr if x.isalpha() and len(x) == 1})


def createTT(n):
    return list(itertools.product([0, 1], repeat=n))


def reverse_table(table):
    return table[::-1]


def prepare(expr):
    """
    turns the expression into a list, using '( )!¬·+-' as delimiters. Case is ignored.
    """
    return [e for e in re.split('([(| |)|!|¬|·|+|-])', expr.upper()) if e != " " and e != ""]


def check_validness(expr):
    if expr.count('(') != expr.count(')'):
        raise BracketException(expr, [expr.count('('), expr.count(')')])


class TruthTable:
    def __init__(self, expr: str, reversed_table=False):
        check_validness(expr)
        self.variables = getVariables(prepare(expr))
        if not self.variables:
            raise InvalidExpressionException('Expression has no valid variable(s) (Must be single letters)')
        self.table = createTT(len(self.variables))
        if reversed_table:
            self.table = reverse_table(self.table)


def main():
    print('Make a truth table:')
    in_ = int(input("Number of variables: "))
    vars_ = []
    for i in range(in_):
        vars_.append(input(f"Variable {i}: "))
    field_names = ['#', *vars_]
    TT = createTT(in_)
    if input('Reverse Table (from all 1s to all 0s) [y/n]? :') == 'y':
        TT.reverse()
    rows = [[i, ] for i in range(len(TT))]
    for i in range(len(rows)):
        rows[i].extend(TT[i])
    pT = PrettyTable()
    pT.field_names = field_names
    pT.add_rows(rows)
    print(pT)


if __name__ == '__main__':
    main()

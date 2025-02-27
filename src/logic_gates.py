from bool_expressions import ExpressionSolver
from parsing import Node, list_expr_to_string, remove_redundant_lists
from truth_table import getVariables


class LogicGateMaker:
    def __init__(self, operator, expr=None):
        self.operator = operator
        self.expr = None
        self.string_expr = None
        if expr:
            self.make_gate_expr(expr)

    def make_gate_expr(self, expr):
        if len(expr) == 1:
            return self.expr
        unifier = globals()[self.operator + 'unifier']()
        unified_expr = unifier.unify(expr)
        self.expr = self._create_NAND_NOR(unified_expr)
        self.string_expr = list_expr_to_string(self.expr)
        return self.string_expr

    def _create_NAND_NOR(self, uniform_expression):
        sign = f'N{self.operator}'

        def invert(expr):
            if len(expr) == 1:
                # no useless parenthesis aroung single variables for readability
                return [expr[0], sign, expr[0]]
            else:
                return [[expr], sign, [expr]]

        def convert(expr: list, invert_nested=None):
            expr = remove_redundant_lists(expr)
            converted_expr = []
            invert_this = None
            for i, x in enumerate(expr):
                # x = remove_redundant_lists(x)
                if not isinstance(x, list):
                    if x == 'NOT':
                        if isinstance(expr[i + 1], list) and expr[i + 1][0] == 'NOT':
                            converted_expr = convert(expr[i + 1][1])  # removes double negations
                            break
                        if len(expr[i + 1]) == 1:  # is variable
                            invert_this = invert_nested = True
                    elif len(x) == 1:
                        converted_expr.append(x)
                    else:
                        converted_expr.append(sign)
                        if invert_nested is None:
                            invert_this = invert_nested = True
                else:
                    nested_expr = convert(x, False)
                    if len(x) == 3 and (i == 0 or expr[i - 1] != 'NOT'):
                        nested_expr = invert(nested_expr)
                    if len(nested_expr) == 1:
                        converted_expr.append(nested_expr[0])
                    else:
                        converted_expr.append(nested_expr)

            if invert_this and invert_nested:
                return invert(converted_expr)
            elif len(expr) == 1 or len(expr) == 2:
                return converted_expr
            return [converted_expr]

        return convert([uniform_expression])


class NandMaker(LogicGateMaker):
    def __init__(self, normal_form=None):
        super().__init__('AND', normal_form)


class NorMaker(LogicGateMaker):
    def __init__(self, normal_form=None):
        super().__init__('OR', normal_form)


class ExpressionUnifier:
    """
    :returns a boolean expression consisting of only 'AND', 'OR' or 'NOT' converted to an expressing consiting only of
    either 'AND' or 'OR' and 'NOT'
    """

    def __init__(self, operator, expr=None):
        self.operator = operator
        self.expr = expr
        self.unified_expr = None
        if expr:
            self.unify(expr)

    def unify(self, expr):
        node = Node(expr)
        tree = node.get_expression_as_lists()
        if self.is_unified(node.get_expression_as_string()):
            return tree
        unified = self._convert(tree)
        self.unified_expr = unified
        return unified

    def _convert(self, expr: list):
        sign = self.operator
        de_morgan = False
        left = None
        right = None
        operator = None
        for i, x in enumerate(expr):
            if x in ['AND', 'OR', 'NOT']:
                operator = x
                de_morgan = (operator != sign and not operator == 'NOT')
            else:
                if isinstance(x, list):
                    x = self._convert(x)
                if left:
                    right = x
                else:
                    left = x
        if de_morgan:
            converted_expr = ['NOT', [[['NOT', left]], sign, ['NOT', right]]]
        else:
            if operator == 'NOT':
                converted_expr = ['NOT', left]
            else:
                converted_expr = [left, sign, right]
        return converted_expr

    def is_unified(self, expr):
        return self.contains_only_NOT(expr) or not self.contains_different_operators(expr, self.operator)

    @staticmethod
    def contains_only_NOT(expr):
        return 'OR' not in expr and 'AND' not in expr

    @staticmethod
    def contains_different_operators(expr, operator):
        return ('OR' in expr and 'AND' in expr) or operator not in expr


def _extract_vars_from_lists_in_parsed_list_expr(parsed_expr):
    string_expr = _list_expr_as_str(parsed_expr)
    vars_ = getVariables(_format_str_expr(string_expr))
    for var in vars_:
        change = True
        while change:
            old_expr = string_expr
            string_expr = string_expr.replace(f'["{var}"]', f'"{var}"', -1)
            change = string_expr != old_expr
    return eval(string_expr)


def _list_expr_as_str(parsed_expr):
    return f"{parsed_expr}".replace("\'", '"', -1)


def _format_str_expr(expr):
    expr = expr.replace('[', '(', -1)
    expr = expr.replace(']', ')', -1)
    expr = expr.replace(',', '', -1)
    expr = expr.replace('"', '', -1)
    return expr


class ANDunifier(ExpressionUnifier):
    def __init__(self, expr=None):
        super().__init__('AND', expr)


class ORunifier(ExpressionUnifier):
    def __init__(self, expr=None):
        super().__init__('OR', expr)


def test():
    test_cases = ['(A OR B)', '(¬A+¬B)·(¬A+B)·(A+B)', '(A and ¬B)', '(¬A+¬B)·(¬A+B)',
                  '(C·D)+(¬A·C)+(¬A·D)+(¬A·¬B)+(¬B·C)',
                  '(¬A·B)·(A+B)+(¬A+B)', 'NOT (A OR B)', '(A)+(B·¬C·D)+(C·¬D)+(¬B·C)+(¬B·¬D)',
                  '((s and not p) and (r or q) or (not(s and not q) and not(r or q)))', 'p or (s or not r)',
                  'p or q or not r or s', 'p or (not q and not s) or (r or( not s and not q)) or (q and not r and s)',
                  '(P)+(Q·¬R·S)+ ((not Q and not S) or R) +(¬Q·¬S)']

    tests = passed = len(test_cases) * 2
    le_print = ''
    for expr in test_cases:
        result = ExpressionSolver().solve(expr)
        NOR = NorMaker(expr)
        NAND = NandMaker(expr)
        NAND_result = ExpressionSolver().solve(NAND.string_expr)
        NOR_result = ExpressionSolver().solve(NOR.string_expr)
        le_print += f'{expr} : {result}\n'
        if NAND_result != result:
            le_print += f'WRONG NAND : {NAND_result}\n'
            passed -= 1
        if NOR_result != result:
            le_print += f'WRONG NOR : {NOR_result})\n'
            passed -= 1
        le_print += f'\n{NOR.string_expr}\n\n{NAND.string_expr}\n'
        le_print += '_____________________________\n'
    le_print += f'Passed test cases ({passed}/{tests})'
    print(f'{le_print}  : LENGTH : {len(le_print)}')


def main():
    # test()
    while True:
        expr = input('Expression: ')
        NA = NandMaker(expr)
        NO = NorMaker(expr)
        print(f'{NA.string_expr}\n\n{NO.string_expr}')


if __name__ == '__main__':
    main()

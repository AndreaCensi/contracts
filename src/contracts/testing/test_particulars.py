from contracts import parse
from contracts.interface import Where, ContractSyntaxError
from contracts.library import *  # @UnusedWildImport
from contracts.syntax import ParseFatalException, ParseException
import unittest


def expression_fails(expression, string, all=True):  # @ReservedAssignment
    try:
        c = expression.parseString(string, parseAll=all)
    except ParseException:
        pass
    except ParseFatalException:
        pass
    else:
        raise Exception('Expression: %s\nparsed to: %s\n(%r)' % 
                        (string, c, c))


def expression_parses(expression, string, all=True):  # @ReservedAssignment
    try:
        expression.parseString(string, parseAll=all)
    except ParseException as e:
        where = Where(string, e.loc)
        msg = 'Error in parsing string: %s' % e
        raise ContractSyntaxError(msg, where=where)
    except ParseFatalException as e:
        where = Where(string, e.loc)
        msg = 'Fatal error in parsing string: %s' % e
        raise ContractSyntaxError(msg, where=where)


class TestParticular(unittest.TestCase):

    def test_variables(self):
        for s in ['a', 'b', 'c', 'd', 'x', 'y']:
            self.assertEqual(parse(s), BindVariable(s, object))
            U = s.upper()
            self.assertEqual(parse(U), BindVariable(U, int))

    def test_variable_parseable(self):
        for s in ['a', 'b', 'c', 'd', 'x', 'y']:
            expression_fails(int_variables_contract, s)
            expression_parses(misc_variables_contract, s)
            U = s.upper()
            expression_parses(int_variables_contract, U)
            expression_fails(misc_variables_contract, U)

    def test_partial(self):
        expression_parses(int_variables_contract, 'A', all=False)
        expression_fails(int_variables_contract, 'A A', all=True)
        expression_parses(int_variables_contract, 'A', all=True)
        expression_fails(int_variables_contract, 'A*', all=False)




class TestBindingVsRef(unittest.TestCase):
    def test_binding_vs_ref(self):
        self.assertEqual(parse('list[N]'), List(BindVariable('N', int), None))

    def test_binding_vs_ref2(self):
        self.assertEqual(parse('N'), BindVariable('N', int))




import unittest

from contracts import (check, ContractNotRespected, Contract, parse,
                       check_multiple, ContractSyntaxError, fail)


class TestIdioms(unittest.TestCase):

    def test_check_1(self):
        res = check('tuple(int,int)', (2, 2))

        assert isinstance(res, dict)

    def test_check_1a(self):
        self.assertRaises(ValueError, check, 1, 2)

    def test_parse_1(self):
        contract = parse('>0')
        assert isinstance(contract, Contract)
        contract.check(2)
        self.assertRaises(ContractNotRespected, contract.check, 'ciao')

    def test_parse_2(self):
        self.assertRaises(ContractSyntaxError, parse, '>>')

    def test_check_2(self):
        self.assertRaises(ContractNotRespected,
                          check, 'tuple(int,int)', (None, 2))

    def test_check_3(self):
        self.assertRaises(ContractSyntaxError,
                          check, 'tuple(>>int,int)', (None, 2))

    def test_check_4(self):
        score = (2, None)
        msg = 'Player score must be a tuple of 2 int.'
        try:
            check('tuple(int,int)', score, msg)
        except ContractNotRespected as e:
            s = str(e)
            assert msg in s
        else:
            assert False

    def test_repr_1(self):
        contract = parse(' list[N](int), N > 0')

        ("%s" % contract)   # => 'list[N](int),N>0'
        ("%r" % contract)   # => And([List(BindVariable('N',int),...

    def test_binding(self):
        context = check('list[N](str), N>0', ['a', 'b', 'c'])

        self.assertTrue('N' in context)
        self.assertTrue(context['N'] == 3)

    def test_check_multiple_1(self):

        data = [[1, 2, 3],
                [4, 5, 6]]
        row_labels = ['first season', 'second season']
        col_labels = ['Team1', 'Team2', 'Team3']

        spec = [('list[C](str),C>0', col_labels),
                ('list[R](str),R>0', row_labels),
                ('list[R](list[C])', data)]
        check_multiple(spec)

        # now with description 
        check_multiple(spec,
                        'I expect col_labels, row_labels, data to '
                        'have coherent dimensions.')

        data = [[1, 2, 3], [1, 2]]
        spec = [('list[C](str),C>0', col_labels),
                ('list[R](str),R>0', row_labels),
                ('list[R](list[C])', data)]

        self.assertRaises(ContractNotRespected, check_multiple, spec)
        self.assertRaises(ContractNotRespected, check_multiple, spec,
                          'my message')

#     def test_symbols(self):
#         from contracts import contract_expression  # @UnusedImport
        # TODO: type

    def test_equality_contract(self):
        c1 = parse('list[C](str),C>0')
        c2 = parse('list[C](str),C>0')
        c3 = parse('list[R](str),R>0')
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)

    def test_equality_rvalue(self):
        c1 = parse('N+1')
        c2 = parse('N+2')
        c3 = parse('P+1')
        self.assertEqual(c1, c1)
        self.assertEqual(c2, c2)
        self.assertEqual(c3, c3)
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertNotEqual(c2, c3)

    def test_check_context(self):
        check('N', 1, N=1)
        fail('N', 1, N=2)

        self.assertRaises(ContractNotRespected, check, 'N', 1, N=2)

        self.assertRaises(ValueError, fail, 'N', 1, N=1)

    def test_check_context2(self):
        """ Variable names must have only one letter. """
        self.assertRaises(ValueError, check, 'N', 1, NN=2)
        self.assertRaises(ValueError, check, 'N', 1, nn=2)


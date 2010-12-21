import unittest



class TestIdioms(unittest.TestCase):
    
    
    def test_check_1(self):
        from contracts import check, Context
  
        res = check('tuple(int,int)', (2, 2))
        
        assert isinstance(res, Context)
  
    def test_parse_1(self):
        from contracts import parse, Contract, ContractNotRespected
  
        # May raise MalformedContract
        contract = parse('>0')
  
        assert isinstance(contract, Contract)
  
        # May raise ContractNotRespected
        contract.check(2)
        

        self.assertRaises(ContractNotRespected, contract.check, 'ciao')
        
    def test_parse_2(self):
        from contracts import parse, ContractSyntaxError

        self.assertRaises(ContractSyntaxError, parse, '>>')

    def test_check_2(self):
        from contracts import check, ContractNotRespected
  
        self.assertRaises(ContractNotRespected,
                          check, 'tuple(int,int)', (None, 2))
  
    def test_check_3(self):
        from contracts import check, ContractSyntaxError
  
        self.assertRaises(ContractSyntaxError,
                          check, 'tuple(>>int,int)', (None, 2))
        
    def test_check_4(self):
        from contracts import check, ContractNotRespected
        score = (2, None)
        msg = 'Player score must be a tuple of 2 int.'
        try: 
            check('tuple(int,int)', score, msg)
        except ContractNotRespected as e:
            s = str(e)
            assert msg in s
        else:
            self.assertFalse()

    def test_repr_1(self):
        from contracts import parse

        contract = parse(' list[N](int), N > 0')     

        ("%s" % contract)   # => 'list[N](int),N>0'
        ("%r" % contract)   # => And([List(BindVariable('N',int),...

    def test_binding(self):
        from contracts import check

        context = check('list[N](str), N>0', ['a', 'b', 'c'])
        
        self.assertTrue('N' in context) 
        self.assertTrue(context['N'] == 3)

    def test_check_multiple_1(self):
        from contracts import check_multiple
        
        data = [[1, 2, 3],
                [4, 5, 6]]
        row_labels = ['first season', 'second season']
        col_labels = ['Team1', 'Team2', 'Team3']
        
        check_multiple([('list[C](str),C>0', col_labels),
                        ('list[R](str),R>0', row_labels),
                        ('list[R](list[C])', data) ])
        
        # now with description 
        check_multiple([('list[C](str),C>0', col_labels),
                        ('list[R](str),R>0', row_labels),
                        ('list[R](list[C])', data) ],
                        'I expect col_labels, row_labels, data to '
                        'have coherent dimensions.')  
                    
    def test_symbols(self):
        from contracts import contract_expression #@UnusedImport

      

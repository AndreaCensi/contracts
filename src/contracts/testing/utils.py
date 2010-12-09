from unittest import TestCase
from contracts import check_contracts, ContractException

class ContractTestCase(TestCase):
    
    def check_contract_ok(self, contract, value):
        check_contracts([contract], [value])
        
    def check_contract_fail(self, contract, value):
        self.assertRaises(ContractException, check_contracts, [contract], [value])
    

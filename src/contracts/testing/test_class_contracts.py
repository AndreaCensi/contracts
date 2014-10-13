from contracts import contract, new_contract, ContractNotRespected
import unittest


class ClassContractsTests(unittest.TestCase):

    def test_class_contract1(self):

        class Game(object):
            def __init__(self, legal):
                self.legal = legal

            @new_contract
            def legal_move1(self, move):
                return move in self.legal

            @contract(move='legal_move1')
            def take_turn(self, move):
                pass

        g1 = Game([1, 2])
        g1.take_turn(1)
        g1.take_turn(2)
        self.assertRaises(ContractNotRespected, g1.take_turn, 3)

    def test_class_contract2(self):

        class Game(object):
            def __init__(self, legal):
                self.legal = legal

            @new_contract
            def legal_move2(self, move):
                return move in self.legal

            @contract(move='legal_move2')
            def take_turn(self, move):
                pass

        g1 = Game([1, 2])
        g1.take_turn(1)
        g1.take_turn(2)
        self.assertRaises(ContractNotRespected, g1.take_turn, 3)

    def test_class_contract3(self):

        class Game(object):
            def __init__(self, legal):
                self.legal = legal

            def legal_move(self, move):
                return move in self.legal

            new_contract('alegalmove', legal_move)

            @contract(move='alegalmove')
            def take_turn(self, move):
                pass

        g1 = Game([1, 2])
        g1.take_turn(1)
        g1.take_turn(2)
        self.assertRaises(ContractNotRespected, g1.take_turn, 3)

    def test_class_contract1_bad(self):
        """ example of bad usage, using the contract from outside """

        class Game(object):
            def __init__(self, legal):
                self.legal = legal

            @new_contract
            def legal_move4(self, move):
                return move in self.legal

        def go():
            @contract(move='legal_move4')
            def take_turn(move):
                pass

            take_turn(0)

        self.assertRaises(ContractNotRespected, go)




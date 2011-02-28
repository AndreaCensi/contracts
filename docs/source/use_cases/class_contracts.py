
# This is an example where the contract depends on the object

from contracts import new_contract, contract

class Game(object):

    def __init__(self, legal_moves):
        self.legal_moves = legal_moves

    # you can now create a contract from object methods
    @new_contract
    def legal_move(self, move):
        if not move in self.legal_moves:
            raise ValueError('Move %r is not valid at this point.' % move)

    @contract(move='legal_move')
    def take_turn(self, move):
        pass
        
        
game = Game(legal_moves=[1,2,3])
game.take_turn(1) # ok
game.take_turn(5) # raises exception

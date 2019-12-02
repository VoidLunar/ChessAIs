import random


class Player:
    def __init__(self, controller="random"):
        # "random", "gp", "alphazero", "*any other we're planning to implement"
        self.controller = controller
        # add any other variables as needed

    def choose_move(self, board, moves, moveDict, gameCount):
#         if self.controller == "random":
#             chosenMoveIndex = random.randint(0, len(moves)-1)
#             chosenMove = moves[chosenMoveIndex]
#             return chosenMove
#         elif self.controller == "qLearn":
            eps = (10000 - gameCount)/10000
            if random.uniform(0,1) < eps:
                chosenMoveIndex = random.randint(0, len(moves)-1)
                chosenMove = moves[chosenMoveIndex]
                return chosenMove
            else: 
                tempHigh = -1.0
                chosenMove = moves[0]
                for move, value in moveDict.items():
                    if (value > tempHigh):
                        value = tempHigh
                        chosenMove = move
                return chosenMove
#         else:
#             # implement controller's movement choice
#             pass
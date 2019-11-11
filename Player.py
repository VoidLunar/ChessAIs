import random


class Player:
    def __init__(self, controller="random"):
        # "random", "gp", "alphazero", "*anyother we're planning to implement"
        self.controller = controller
        # add any other variables as needed

    def choose_move(self, board, moves):
        if self.controller == "random":
            chosenMoveIndex = random.randint(0, len(moves)-1)
            chosenMove = moves[chosenMoveIndex]
            return chosenMove

        else:
            # implement controller's movement choice
            pass

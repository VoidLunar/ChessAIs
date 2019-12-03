import random
from stockfish import Stockfish
import chess

class Player:
    def __init__(self, controller="random", customFunction=None):
        # "random", "gp", "alphazero", "*any other we're planning to implement"
        self.controller = controller
        self.customFunction = customFunction
        # add any other variables as needed
        self.stockfish = Stockfish('./stockfish-10-win/Windows/stockfish_10_x64.exe')

    def choose_move(self, board, moves):
        if self.controller == "random":
            chosenMoveIndex = random.randint(0, len(moves)-1)
            chosenMove = moves[chosenMoveIndex]
            return chosenMove
        elif self.controller == "custom":
            return self.customFunction(board, moves)
        elif self.controller == "stockfish":
            self.stockfish.set_fen_position(board.fen())
            uciStr = self.stockfish.get_best_move()
            move = chess.Move.from_uci(uciStr)
            return move
        elif self.controller == "player":
            while True:
                print(board)
                move = input("Input a move, or input m for a list of possible moves: ")
                if move == 'm':
                    for move in moves:
                        print(move)
                    continue
                try:
                    move = chess.Move.from_uci(move)
                    if move in moves:
                        return move
                    else:
                        print("Invalid move")
                except:
                    print("Invalid move")
                    continue
        else:
            # implement controller's movement choice
            pass
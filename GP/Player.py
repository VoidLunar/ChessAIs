import random
from stockfish import Stockfish
import chess
from Alphazero.game import GameState, chessMoves


class Player:
    def __init__(self, controller="random", customFunction=None, agent=None):
        # "random", "gp", "alphazero", "*anyother we're planning to implement"
        self.controller = controller
        self.customFunction = customFunction
        # add any other variables as needed
        self.stockfish = Stockfish('./stockfish-10-win/Windows/stockfish_10_x64.exe')
        self.isNNSetup = False
        self.agent = agent

    def choose_move(self, board, moves):
        if self.controller == "random":
            chosenMoveIndex = random.randint(0, len(moves)-1)
            chosenMove = moves[chosenMoveIndex]
            return chosenMove
        elif self.controller == "custom":
            return self.customFunction(board, moves)

        #neuralnetwork controller. makesure to pass in the agent when declaring the player
        elif self.controller == "nn":
            if not self.isNNSetup:
                self.state = GameState(board)
                self.isNNSetup = True
            return self.customFunction(self.state, self.agent)

        elif self.controller == "az":
            if not self.isNNSetup:
                self.state = GameState(board)
                self.isNNSetup = True
            action, _, _, _ = self.customFunction(self.state, self.agent)
            moveFrom = int(action / len(chessMoves))

            chessMoveIndex = action % len(chessMoves)
            movedistance = chessMoves[chessMoveIndex]

            isPawn = True if board.piece_at(moveFrom) is not None and str(
                board.piece_at(moveFrom)).lower() == 'p' else False
            promo = None
            # regular promo
            # promo is int 2 = knight, 3 = bishop, 4 = rook, 5 = queen
            if isPawn:
                if [8, 9, 10, 11, 12, 13, 14, 15].count(moveFrom) > 0:
                    if movedistance == -9 or movedistance == -8 or movedistance == -7:
                        promo = chess.QUEEN
                    elif movedistance > 100:
                        promo = int(movedistance / 100)
                        if promo == 2:
                            promo = chess.KNIGHT
                        elif promo == 3:
                            promo = chess.BISHOP
                        else:
                            promo = chess.ROOK
                        movedistance = (movedistance % 100) * -1

                elif [48, 49, 50, 51, 52, 53, 54, 55].count(moveFrom) > 0:
                    if movedistance == 9 or movedistance == 8 or movedistance == 7:
                        promo = chess.QUEEN
                    elif movedistance > 100:
                        promo = int(movedistance / 100)
                        if promo == 2:
                            promo = chess.KNIGHT
                        elif promo == 3:
                            promo = chess.BISHOP
                        else:
                            promo = chess.ROOK
                        movedistance = movedistance % 100
            moveTo = moveFrom + movedistance
            # print("move from =",moveFrom, "move to =", moveTo, "distance =",movedistance)
            move = chess.Move(moveFrom, moveTo, promo)
            return move

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


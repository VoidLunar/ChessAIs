import copy

import chess
import numpy as np
import logging

import numpy as np
import tensorflow as tf

from AI import get_legal_moves


class Game:
    def __init__(self):
        self.gameState = GameState()
        self.grid_shape = (8, 8)
        self.input_shape = (56, 8, 8) #12 * t + 8
        self.name = 'chess'
        self.state_size = 7.7 * (10 ** 45)
        self.action_size = 8*8*73

    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)
        self.gameState = next_state
        info = None
        return ((next_state, value, done, info))

    def identities(self, state, actionValues):
        currentBoard = state.board
        currentAV = actionValues
        identities = [(GameState(currentBoard, state.playerTurn), currentAV)]

        return identities

    def reset(self):
        board = chess.Board()
        self.gameState = GameState(board)

class GameState():
    def __init__(self, board=None, playerTurn=1):
        self.board = chess.Board()
        self.t = 4
        # board dimension (8x8) and
        # t history of black,white position for each player \
        # plus 1 layer for current player's turn,
        # plus 2 repetition, move count, 2+2 castling, and no progress count
        # self.input_dim = (8, 8, 12 * self.t + 8)
        # history of board state saved up to t
        self.wh = []
        self.bh = []
        # each of these represent a layer
        self.wRepeat = np.zeros((8, 8))
        self.bRepeat = np.zeros((8, 8))
        self.color = np.ones((8, 8))
        # may not need movecount for my purpose. may remove later? idk
        self.moveCount = 0

        self.wQCastling = np.ones((8, 8))
        self.wKCastling = np.ones((8, 8))
        self.bQCastling = np.ones((8, 8))
        self.bKCastling = np.ones((8, 8))
        self.noProgressCount = np.zeros((8, 8))
        if board is not None:
            self.get_board(board)

    def get_board(self, board):
        self.board = board
        bPl, bRl, bNl, bBl, bQl, bKl, wPl, wRl, wNl, wBl, wQl, wKl = (np.zeros((8, 8)) for i in range(12))
        blackBoard = [bPl, bRl, bNl, bBl, bQl, bKl]
        whiteBoard = [wPl, wRl, wNl, wBl, wQl, wKl]

        # update three fold repetition layer
        # white's turn
        if board.turn:
            if board.can_claim_threefold_repetition():
                if self.wRepeat[0][0] == 0:
                    self.wRepeat += 1
            else:
                if self.wRepeat[0][0] == 0:
                    self.wRepeat -= 1
            # color layer is all 0 for white
            self.color = np.zeros((8, 8))
            # update castling layer
            self.update_castling(board)

        # black's turn
        else:
            if board.can_claim_threefold_repetition():
                if self.bRepeat[0][0] == 0:
                    self.bRepeat += 1
            else:
                if self.bRepeat[0][0] == 1:
                    self.bRepeat -= 1
            # color layer is all 0 for white
            self.color = np.ones((8, 8))
            # update castling layer
            self.update_castling(board)

        # update board state
        for i in range(0, 8):
            for j in range(0, 8):
                piece = board.piece_at(i * 8 + j)
                if piece is not None:
                    piece = piece.symbol()
                    # white piece
                    if piece.isupper():
                        if piece == 'P':
                            wPl[i][j] = 1
                        elif piece == 'R':
                            wRl[i][j] = 1
                        elif piece == 'N':
                            wNl[i][j] = 1
                        elif piece == 'B':
                            wBl[i][j] = 1
                        elif piece == 'Q':
                            wQl[i][j] = 1
                        elif piece == 'K':
                            wKl[i][j] = 1
                    # black piece
                    else:
                        if piece == 'p':
                            bPl[i][j] = 1
                        elif piece == 'r':
                            bRl[i][j] = 1
                        elif piece == 'n':
                            bNl[i][j] = 1
                        elif piece == 'b':
                            bBl[i][j] = 1
                        elif piece == 'q':
                            bQl[i][j] = 1
                        elif piece == 'k':
                            bKl[i][j] = 1

        self.bh.insert(0, blackBoard)
        self.wh.insert(0, whiteBoard)
        if len(self.bh) < self.t:
            while len(self.bh) < self.t:
                self.bh.insert(0, blackBoard)

        if len(self.wh) < self.t:
            while len(self.wh) < self.t:
                self.wh.insert(0, whiteBoard)

        # remove history past t
        if len(self.bh) > self.t:
            self.bh.pop(len(self.bh) - 1)
        if len(self.wh) > self.t:
            self.wh.pop(len(self.wh) - 1)

        self.moveCount = len(board.move_stack)

        self.noProgressCount.fill(board.halfmove_clock)

        self.allowedActions = self._allowedActions()
        self.allowedActionsReadable = self._allowedActionsReadable()
        self.playerTurn = self._getTurn()
        self.isEndGame = len(self.board.move_stack) > 5 or self.board.is_game_over()  # 269
        self.value = self._getValue()
        self.score = self._getScore()
        self.id = self._convertStateToId()

    def update_castling(self, board):
        if board.turn:
            if not board.has_queenside_castling_rights(board.turn):
                if self.wQCastling[0][0] == 1:
                    self.wQCastling -= 1
            if not board.has_kingside_castling_rights(board.turn):
                if self.wKCastling[0][0] == 1:
                    self.wKCastling -= 1
        else:
            if not board.has_queenside_castling_rights(board.turn):
                if self.bQCastling[0][0] == 1:
                    self.bQCastling -= 1
            if not board.has_kingside_castling_rights(board.turn):
                if self.bKCastling[0][0] == 1:
                    self.bKCastling -= 1

    def _convertStateToId(self):
        id = str(self.board)

        return id

    def to_stack(self):
        x = []
        for wh in self.wh:
            for pieceLocation in wh:
                x.append(pieceLocation)

        for bh in self.bh:
            for pieceLocation in bh:
                x.append(pieceLocation)
        x.append(self.color)
        x.append(self.wRepeat)
        x.append(self.bRepeat)
        x.append(self.wKCastling)
        x.append(self.wQCastling)
        x.append(self.bKCastling)
        x.append(self.bQCastling)
        x.append(self.noProgressCount)
        gameStateStack = tf.stack(x)
        return gameStateStack

    def _allowedActions(self):
        legal_moves = get_legal_moves(self.board.legal_moves)
        for move in legal_moves:
            #dont put yourself into check.
            if self.board.is_into_check(move):
                legal_moves.remove(move)
        legal_moves = self._shape_legal_moves(legal_moves)
        return legal_moves

    def _allowedActionsReadable(self):
        legal_moves = get_legal_moves(self.board.legal_moves)
        for move in legal_moves:
            if self.board.is_into_check(move):
                legal_moves.remove(move)
        return legal_moves

    def _shape_legal_moves(self, legal_moves):
        lm = []
        for move in legal_moves:
            # ignore moves that would put yourself into check

            move = move.xboard()
            #abcdefgh
            moveFromFile = chess.FILE_NAMES.index(move[0])
            #12345678
            moveFromRank = chess.RANK_NAMES.index(move[1])
            moveFrom = moveFromFile + moveFromRank*8

            moveToFile = chess.FILE_NAMES.index(move[2])
            moveToRank = chess.RANK_NAMES.index(move[3])
            moveTo = moveToFile + moveToRank * 8

            distance = moveTo - moveFrom
            if len(move) > 4:
                promote = move[4]
                distance = abs(distance)
                # distance = distance + (promotion(int) * 100)
                if promote == 'r':
                    distance += 400
                elif promote == 'n':
                    distance += 200
                else:
                    distance += 300
            chessmoveindex = chessMoves.index(distance)
            lm.append(moveFrom * len(chessMoves) + chessmoveindex)
        return lm

    def _getValue(self):
        # This is the value of the state for the current player
        # i.e. if the previous player played a winning move, you lose
        if self.board.is_checkmate():
            # Black wins
            if self.board.turn:
                return (-1, -1, 1)
            # White wins
            else:
                return (-1, 1, -1)
        return (0, 0, 0)

    def _getTurn(self):
        if self.board.turn:
            return 1
        else:
            return -1

    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2])

    def takeAction(self, action):
        moveFrom = int(action / len(chessMoves))

        chessMoveIndex = action % len(chessMoves)
        movedistance = chessMoves[chessMoveIndex]

        isblackPawn = True if self.board.piece_at(moveFrom) is not None and self.board.piece_at(moveFrom) == 'p' else False
        isWhitePawn = True if self.board.piece_at(moveFrom) is not None and self.board.piece_at(moveFrom) == 'P' else False
        promo = None

        # regular promo
        # promo is int 2 = knight, 3 = bishop, 4 = rook, 5 = queen
        if [8,9,10,11,12,13,14,15].count(moveFrom) > 0 and isblackPawn:
            if movedistance == -9 or movedistance == -8 or movedistance == -7:
                promo = chess.QUEEN
            else:
                promo = int(movedistance/100)
                if promo == 2:
                    promo = chess.KNIGHT
                elif promo == 3:
                    promo = chess.BISHOP
                else:
                    promo = chess.ROOK
                movedistance = movedistance % -100

        elif [48,49,50,51,52,53,54,55].count(moveFrom) > 0 and isWhitePawn:
            if movedistance == 9 or movedistance == 8 or movedistance == 7:
                promo = chess.QUEEN
            else:
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

        b = copy.deepcopy(self.board)
        b.push(move)

        newState = GameState(b)

        value = 0
        done = 0

        if newState.isEndGame:
            value = newState.value[0]
            done = 1

        return (newState, value, done)

    def render(self, logger):

        logger.info(self.board)
        logger.info('--------------')


chessMoves = []
up = [i*8 for i in range(1, 8)]
down = [i*-8 for i in range(1, 8)]
left = [i for i in range(1, 8)]
right = [-i for i in range(1, 8)]
upLeft = [i*7 for i in range(1, 8)]
upRight = [i*9 for i in range(1, 8)]
DownLeft = [i*-9 for i in range(1, 8)]
DownRight = [i*-7 for i in range(1, 8)]

nUpLeft = 15
nUpRight = 17
nDownLeft = -17
nDownRight = -15
nLeftUp = 6
nLeftDown = -10
nRightUp = 10
nRightDown = -6
underPromo = [207, 208, 209, 307, 308, 309, 407, 408, 409]

knightMove = [nUpLeft, nUpRight, nDownLeft, nDownRight, nLeftUp, nLeftDown, nRightUp, nRightDown]
chessMoves.extend(up)
chessMoves.extend(down)
chessMoves.extend(left)
chessMoves.extend(right)
chessMoves.extend(upLeft)
chessMoves.extend(upRight)
chessMoves.extend(DownLeft)
chessMoves.extend(DownRight)
chessMoves.extend(knightMove)
chessMoves.extend(underPromo)
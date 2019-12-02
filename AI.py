import chess
import csv
from Player import Player
from stockfish import Stockfish

qTable = dict()

# player1 = white piece. moves first    (chess.WHITE (TRUE))
# player2 = black piece                 (chess.BLACK (FALSE))
def play(player1: Player, player2: Player):
    stockfish = Stockfish('/Users/chessWork/stockfish-10-win/Windows/stockfish_10_x64')
    draw = False
    board = chess.Board()

    turn = 0
    while True:
        turn = turn + 1
        # move white (upper case)
        possible_moves = get_legal_moves(board.legal_moves)
        
        currentState = board.fen()
        if currentState not in qTable.keys():
            moveDict = dict()
            for move in possible_moves:
                moveDict[move] = 0.0
            qTable[currentState] = moveDict
        moveDict = qTable[currentState]
        p1Move = player1.choose_move(board, possible_moves, moveDict, gameCount)
        boardBefore = board.copy()
        board.push(p1Move)

        # check if game is over by p1's move
        if board.is_game_over():
            break

        # move black (lower case)
        stockfish.set_fen_position(board.fen())
        uciStr = stockfish.get_best_move()
        p2Move = chess.Move.from_uci(uciStr)
        board.push(p2Move)
        scorePoints = score(boardBefore, board)

        futureState = board.fen()
        tempHigh = 0.0
        futureValue = 0.0
        if futureState not in qTable.keys():
            futureValue = 0.0
        else:
            for move, value in qTable[futureState].items():
                if (value > tempHigh):
                    futureValue = value
        
        newValue = moveDict[p1Move] + 0.7 * (scorePoints + 0.99 * futureValue - moveDict[p1Move])
        qTable[currentState][p1Move] = newValue

        # check if game is over by p2's move
        if board.is_game_over():
            turnList.append(turn)
            break

    gec = get_game_ending_condition(board)
    # do something with game ending condition. ( reward winner/ adjust probability etc )


def get_game_ending_condition(board):
    gec = ""
    if board.is_checkmate():
        if board.turn:
            gec = "Black (Stockfish) checkmates White (Random AI)"
            gecList[0] = gecList[0] + 1
        else:
            gec = "White (Random AI) checkmates Black (Stockfish)"
            gecList[1] = gecList[1] + 1
            print("Game Number: " + str(gameCount))
            print("Omg we won")
        pass
    elif board.is_stalemate():
        gec = "Stalemate"
        gecList[2] = gecList[2] + 1
        pass
    elif board.is_insufficient_material():
        gec = "Insufficient pieces to end the game"
        gecList[3] = gecList[3] + 1
        pass
    elif board.is_fivefold_repetition():
        gec = "five fold repetition (draw)"
        gecList[4] = gecList[4] + 1
        print("Draw Game Number: " + str(gameCount))
        pass
    elif board.is_seventyfive_moves():
        gec = "seventy five move rule (draw)"
        gecList[5] = gecList[5] + 1
    return gec


def get_legal_moves(legal_moves):
    moves = []
    for move in legal_moves:
        moves.append(move)
    return moves

def score(beforeBoard, afterBoard):
    beforeBoardDict = beforeBoard.piece_map()
    afterBoardDict = afterBoard.piece_map()
    whiteBeforePoints = 0
    whiteAfterPoints = 0
    blackBeforePoints = 0
    blackAfterPoints = 0
    
    for square in beforeBoardDict:
        piece = beforeBoard.piece_at(square)
        if (piece.color == True):
            whiteBeforePoints += piece.piece_type
        else:
            blackBeforePoints += piece.piece_type
     
    for square in afterBoardDict:
        piece = afterBoard.piece_at(square)
        if (piece.color == True):
            whiteAfterPoints += piece.piece_type
        else:
            blackAfterPoints += piece.piece_type
    
    scorePoints = (whiteAfterPoints - whiteBeforePoints) + (blackBeforePoints - blackAfterPoints)
    return scorePoints

def run():
    p1 = Player()
    p2 = Player()
    play(p1, p2)

gecList = [0, 0, 0, 0, 0, 0]
turnList = []
gameCount = 0
while (gameCount < 10000):
    run()
    gameCount += 1


moveCount = 0 
for number in turnList:
        moveCount += number
print("Move Count:" + str(moveCount))
print("Turn List: " + str(turnList))  
turnList.sort()
print("Sorted Turn List: " + str(turnList))
print("QTable Size:" + str(len(qTable)))
print("[Stockfish wins, AI wins, stalemate, insufficient pieces to end the game, five fold repetition draw, 75 move rule draw]")
print(str(gecList))

with open('qTable.txt', 'a') as the_file:
    for key, values in qTable.items():
        the_file.write(str(key) + ',')
        for key2 in values:
            the_file.write(str(key2) + ',' + str(values[key2]) + ',')
        the_file.write('\n')
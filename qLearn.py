import random
import chess
from Player import Player
import csv

def getQTable(): #For the analysisVersusFile
    importName = 'qTable.csv'
    
    importFile = open(importName, 'rt')
    
    reader = csv.reader(importFile)
    
    qTable = dict()
    moveDict = dict()
    index = 1
    for row in reader:
        while (index < len(row) - 1):
            moveDict[row[index]] = row[index + 1]
            index = index + 2
        qTable[row[0]] = moveDict
        moveDict.clear()
    
    return qTable

def pickQChessMove(board, moves):
    qTable = getQTable()
    
    currentState = board.fen()
    
    if (currentState not in qTable.keys()):
        chosenMoveIndex = random.randint(0, len(moves)-1)
        chosenMove = moves[chosenMoveIndex]
    else: 
        moveDict = qTable[currentState]
        tempHigh = -1.0
        chosenMove = moves[0]
        for move, value in moveDict.items():
            if (value > tempHigh):
                value = tempHigh
                chosenMove = move
    
    return chosenMove

totalGames = 10000
qTable = dict()
# player1 = white piece. moves first    (chess.WHITE (TRUE))
# player2 = black piece                 (chess.BLACK (FALSE))
def play(player1: Player, player2: Player):
    draw = False
    board = chess.Board()

    turn = 0
    while True:
        turn = turn + 1
        # move white (upper case)
        #qLearn is White
        if (player2.controller == "stockfish"):
            possible_moves = get_legal_moves(board.legal_moves)
            currentState = board.fen()
            if currentState not in qTable.keys():
                moveDict = dict()
                for move in possible_moves:
                    moveDict[move] = 0.0
                qTable[currentState] = moveDict
            moveDict = qTable[currentState]
            
            #Pick move
            eps = (totalGames - gameCount)/totalGames
            if random.uniform(0,1) < eps:
                chosenMoveIndex = random.randint(0, len(possible_moves)-1)
                chosenMove = possible_moves[chosenMoveIndex]
            else: 
                tempHigh = -1.0
                chosenMove = possible_moves[0]
                for move, value in moveDict.items():
                    if (value > tempHigh):
                        value = tempHigh
                        chosenMove = move
            p1Move = chosenMove
            #p1Move = player1.choose_move(board, possible_moves)
            boardBefore = board.copy()
            board.push(p1Move)
    
            # check if game is over by p1's move
            if board.is_game_over():
                break
    
            # move black (lower case)
            board = board.mirror()
            possible_moves = get_legal_moves(board.legal_moves)
            p2Move = player2.choose_move(board, possible_moves)
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
        else: #QLearn is Black
            possible_moves = get_legal_moves(board.legal_moves)
            p1Move = player1.choose_move(board, possible_moves)
            board.push(p1Move)
            
            boardBefore = board.copy()
            
            # check if game is over by p1's move
            if board.is_game_over():
                break
    
            # move black (lower case)
            board = board.mirror()
            
            possible_moves = get_legal_moves(board.legal_moves)
            currentState = board.fen()
            if currentState not in qTable.keys():
                moveDict = dict()
                for move in possible_moves:
                    moveDict[move] = 0.0
                qTable[currentState] = moveDict
            moveDict = qTable[currentState]
            
            #Pick move
            eps = (totalGames - gameCount)/totalGames
            if random.uniform(0,1) < eps:
                chosenMoveIndex = random.randint(0, len(possible_moves)-1)
                chosenMove = possible_moves[chosenMoveIndex]
            else: 
                tempHigh = -1.0
                chosenMove = possible_moves[0]
                for move, value in moveDict.items():
                    if (value > tempHigh):
                        value = tempHigh
                        chosenMove = move
            p2Move = chosenMove
            #p2Move = player2.choose_move(board, possible_moves)
            board.push(p2Move)
    
            scorePoints = score(boardBefore, board)
    
            board = board.mirror()
            possible_moves = get_legal_moves(board.legal_moves)
            p1Move = player1.choose_move(board, possible_moves)
            board.push(p1Move)
            
            futureState = board.fen()
            tempHigh = 0.0
            futureValue = 0.0
            if futureState not in qTable.keys():
                futureValue = 0.0
            else:
                for move, value in qTable[futureState].items():
                    if (value > tempHigh):
                        futureValue = value
            
            newValue = moveDict[p2Move] + 0.7 * (scorePoints + 0.99 * futureValue - moveDict[p2Move])
            qTable[currentState][p2Move] = newValue
            
            board.pop()
            board = board.mirror()

        # check if game is over by p2's move
        if board.is_game_over():
            turnList.append(turn)
            board = board.mirror()
            break

        board = board.mirror()

    gec = get_game_ending_condition(board)
    return board
    # do something with game ending condition. ( reward winner/ adjust probability etc )


def get_game_ending_condition(board):
    gec = ""
    if board.is_checkmate():
        if board.turn:
            gec = "Black checkmates White"
            if (gameCount < (totalGames / 2)):
                gecList[0] = gecList[0] + 1
#                 print("Stockfish is Black")
#                 print(gec)
            else:
                gecList[1] = gecList[1] + 1
        else:
            gec = "White checkmates Black"
            if (gameCount < totalGames / 2):
                gecList[1] = gecList[1] + 1
            else:
                gecList[0] = gecList[0] + 1
#                 print("Stockfish is White")
#                 print(gec)
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
    
    #If QLearn is White
    if (gameCount < totalGames / 2):
        scorePoints = (whiteAfterPoints - whiteBeforePoints) + (blackBeforePoints - blackAfterPoints)
    #If QLearn is Black
    else:
        scorePoints = (blackAfterPoints - blackBeforePoints) + (whiteBeforePoints - whiteAfterPoints)
    return scorePoints

# def run():
#     if (gameCount < totalGames / 2):
#         p1 = Player()
#         p2 = Player("stockfish")
#     else:
#         p1 = Player("stockfish")
#         p2 = Player()
#     play(p1, p2)
 
# gecList = [0, 0, 0, 0, 0, 0]
# turnList = []
# gameCount = 0
# while (gameCount < totalGames):
#     run()
#     gameCount += 1
 
 
# moveCount = 0 
# for number in turnList:
#         moveCount += number
# print("Move Count:" + str(moveCount))
# print("Turn List: " + str(turnList))  
# turnList.sort()
# print("Sorted Turn List: " + str(turnList))
# print("QTable Size:" + str(len(qTable)))
# print("[Stockfish wins, AI wins, stalemate, insufficient pieces to end the game, five fold repetition draw, 75 move rule draw]")
# print(str(gecList))

with open('qTable.txt', 'a') as the_file:
    for key, values in qTable.items():
        the_file.write(str(key) + ',')
        for key2 in values:
            the_file.write(str(key2) + ',' + str(values[key2]) + ',')
        the_file.write('\n')

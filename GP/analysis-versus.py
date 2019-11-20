from Player import Player
from AI import play
from chessGP import fileToGPTree

randomTree = fileToGPTree('./solutions/randomSolution.txt')
stockfishTree = fileToGPTree('./solutions/stockfishSolution.txt')

randomPlayer = Player('custom', randomTree.pickChessMove)
stockfishPlayer = Player('custom', stockfishTree.pickChessMove)

win = 0
draw = 0
loss = 0
for i in range(25):
    resultBoard = play(stockfishPlayer, randomPlayer)
    result = resultBoard.result()
    print(result)
    if result == '1-0':
        win += 1
    elif result == '0-1':
        loss += 1
    else:
        draw += 1
print("White: Stockfish, Black: Random")
print(win, draw, loss)
win = 0
draw = 0
loss = 0
for i in range(25):
    resultBoard = play(randomPlayer, stockfishPlayer)
    result = resultBoard.result()
    if result == '1-0':
        win += 1
    elif result == '0-1':
        loss += 1
    else:
        draw += 1
print("White: Random, Black: Stockfish")
print(win, draw, loss)
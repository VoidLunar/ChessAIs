from Player import Player
from AI import play
from qLearn import pickQChessMove



qLearnPlayer = Player('custom', pickQChessMove)
stockfishPlayer = Player('stockfish')
 
win = 0
draw = 0
loss = 0
for i in range(25):
    resultBoard = play(stockfishPlayer, qLearnPlayer)
    result = resultBoard.result()
    print(result)
    if result == '1-0':
        win += 1
    elif result == '0-1':
        loss += 1
    else:
        draw += 1
print("White: Stockfish, Black: qLearn")
print(win, draw, loss)
win = 0
draw = 0
loss = 0
for i in range(25):
    resultBoard = play(qLearnPlayer, stockfishPlayer)
    result = resultBoard.result()
    if result == '1-0':
        win += 1
    elif result == '0-1':
        loss += 1
    else:
        draw += 1
print("White: qLearn, Black: Stockfish")
print(win, draw, loss)
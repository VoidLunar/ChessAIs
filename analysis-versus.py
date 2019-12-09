from Player import Player
from AI import play
from chessGP import fileToGPTree
from qLearn import QThing




randomTree = fileToGPTree('./solutions/randomSolution.txt')
stockfishTree = fileToGPTree('./solutions/stockfishSolution.txt')

players = []

q = QThing()
qLearnPlayer = Player('custom', q.pickQChessMove)
qLearnPlayer.name = "Q"
players.append(qLearnPlayer)
randomPlayer = Player('custom', randomTree.pickChessMove)
randomPlayer.name = "GP-Random"
players.append(randomPlayer)
stockfishPlayer = Player('custom', stockfishTree.pickChessMove)
stockfishPlayer.name = "GP-Stockfish"
players.append(stockfishPlayer)
realRandomPlayer = Player('random')
realRandomPlayer.name = 'random'
players.append(realRandomPlayer)
realStockfishPlayer = Player('stockfish')
realStockfishPlayer.name = 'stockfish'
players.append(realStockfishPlayer)

resultString = ""

for wplayer in players:
    for bplayer in players:
        win = 0
        draw = 0
        loss = 0
        for i in range(25):
            resultBoard = play(wplayer, bplayer)
            result = resultBoard.result()
            if result == '1-0':
                win += 1
            elif result == '0-1':
                loss += 1
            else:
                draw += 1
        print("White: " + wplayer.name + ", Black: " + bplayer.name)
        print(win, draw, loss)
        resultString += ("White: " + wplayer.name + ", Black: " + bplayer.name + "\n")
        resultString += str(win) + '\t' + str(draw) + '\t' + str(loss) + '\n'
        
resultString += "\n"
for player in players:
    resultString += 'Player: ' + str(player.name)
    resultString += 'Moves made: ' + str(player.movesMade)
    resultString += 'Total time: ' + str(player.timeSpent)
    resultString += 'Avg. Time per move: ' + str(player.timeSpent / player.movesMade)
    resultString += '\n'
file = open('vsResults', 'w')
file.write(resultString)
        

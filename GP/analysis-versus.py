from Alphazero.NN import nnMove
from Alphazero.agent import Agent
from Alphazero.game import Game
from Alphazero.model import Residual_CNN
from GP.Player import Player
from AI import play
from chessGP import fileToGPTree
import config

randomTree = fileToGPTree('./solutions/randomSolution.txt')
stockfishTree = fileToGPTree('./solutions/stockfishSolution.txt')

randomPlayer = Player('custom', randomTree.pickChessMove)
stockfishPlayer = Player('custom', stockfishTree.pickChessMove)

env = Game()
#run_archive_folder + game + '/run' + str(run_number).zfill(4) + "/models/version" + "{0:0>4}".format(version) + '.h5')
NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape, env.action_size, config.HIDDEN_CNN_LAYERS)
m_tmp = NN.read(env.name, '', 1)
agent = Agent('player1', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, NN)
nnPlayer = Player('nn', agent, nnMove)
azPlayer = Player('az', agent, agent.act)

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
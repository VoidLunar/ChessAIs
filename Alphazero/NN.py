import copy
import pickle
import random

import chess
import numpy as np

from AI import get_legal_moves, get_game_ending_condition
from Alphazero.game import Game
import Alphazero.config as config
from Alphazero.agent import Agent
from Alphazero.memory import Memory

from Alphazero.model import Residual_CNN
from Alphazero.settings import run_folder
from GP.Player import Player

def nnMove(state, agent, tau=0):
    value, pi, allowedActions = agent.get_preds(state)
    probs = pi[allowedActions]
    #deterministic
    if tau == 0:
        # take max probability
        actions = np.argwhere(probs == max(probs))
        moveIndex = random.choice(actions)[0]
    #random
    else:
        moveIndex = random.randint(0, len(probs)-1)
    lms = get_legal_moves(state.board.legal_moves)
    move = lms[moveIndex]
    policyIndex = allowedActions[moveIndex]
    return move, value, pi, policyIndex

def train(player1: Player, player2: Player, numEpisode):
    for episode in range(numEpisode):
        print("Game#", numGame + episode + 1)
        board = chess.Board()
        memory.clear_stmemory()
        env.gameState.get_board(board)

        values = []
        while True:
            capture = False
            value = 0
            # move white
            if len(board.move_stack) % 30 == 0:
                print("board at move:", len(board.move_stack))
                print(board)
            possible_moves = get_legal_moves(board.legal_moves)
            if len(board.move_stack) < config.TURNS_UNTIL_TAU0:
                p1Move, value, probs, policyIndex = nnMove(env.gameState, player1.agent, 1)
            else:
                p1Move, value, probs, policyIndex = nnMove(env.gameState, player1.agent, 0)
            board.push(p1Move)
            values.append(value)
            env.gameState.get_board(board)
            memory.commit_stmemory(copy.deepcopy(env.identities), env.gameState, probs, policyIndex)

            # check if game is over by p1's move
            if board.is_game_over():
                break
            # print("White moved")
            # print(board)
            # move black
            possible_moves = get_legal_moves(board.legal_moves)
            if len(board.move_stack) < config.TURNS_UNTIL_TAU0:
                p2Move, value, probs, policyIndex = nnMove(env.gameState, player2.agent, 1)
            else:
                p2Move, value, probs, policyIndex = nnMove(env.gameState, player2.agent, 0)
            board.push(p2Move)
            values.append(value)
            env.gameState.get_board(board)
            memory.commit_stmemory(copy.deepcopy(env.identities), env.gameState, probs, policyIndex)

            if board.is_game_over():
                break

        # if game is not draw,
        if board.is_checkmate():
            #### If the game is finished, assign the values correctly to the game moves
            for move in memory.stmemory:
                # loser move value = -1
                if move['playerTurn'] == env.gameState.playerTurn:
                    move['value'] = -1
                    # decrease policy probablity of losing move
                    move['AV'][move['policyIndex']] = move['AV'][move['policyIndex']] - 0.1
                    if move['AV'][move['policyIndex']] < 0:
                        move['AV'][move['policyIndex']] = 0
                # winner move value = 1
                else:
                    move['value'] = 1
                    # increase policy probablity of winning move
                    move['AV'][move['policyIndex']] = move['AV'][move['policyIndex']] + 0.1
                    if move['AV'][move['policyIndex']] > 1:
                        move['AV'][move['policyIndex']] = 1
            if env.gameState.board.turn:
                print("white won")
            else:
                print("black won")
        else:
            print("draw")
            for i in range(0, len(memory.stmemory)):
                memory.stmemory[i]['value'] = values[i]
        print("endBoard")
        print(board)
        memory.commit_ltmemory()

        print("Memory length:", len(memory.ltmemory))
        print("Memory Threashold:", config.MEMORY_SIZE)

def compete(player1: Player, player2: Player, numCompeteGames):
    p1score = [0, 0, 0]
    for competeGame in range(0, numCompeteGames):
        print("Game#", numGame + competeGame + 1)
        draw = False
        board = chess.Board()
        env.gameState.get_board(board)
        p1Start = numGame > 0
        while True:
            # move white
            if p1Start:
                if len(board.move_stack) < config.TURNS_UNTIL_TAU0:
                    p1Move, value, _, _ = nnMove(env.gameState, player1.agent, 1)
                else:
                    p1Move, value, _, _ = nnMove(env.gameState, player1.agent, 0)
                board.push(p1Move)
            else:
                if len(board.move_stack) < config.TURNS_UNTIL_TAU0:
                    p2Move, value, _, _ = nnMove(env.gameState, player2.agent, 1)
                else:
                    p2Move, value, _, _ = nnMove(env.gameState, player2.agent, 0)
                board.push(p2Move)
            env.gameState.get_board(board)

            if board.is_game_over():
                break
            # move black
            if p1Start:
                if len(board.move_stack) < config.TURNS_UNTIL_TAU0:
                    p2Move, value, _, _ = nnMove(env.gameState, player2.agent, 1)
                else:
                    p2Move, value, _, _ = nnMove(env.gameState, player2.agent, 0)
                board.push(p2Move)

            else:
                if len(board.move_stack) < config.TURNS_UNTIL_TAU0:
                    p1Move, value, _, _ = nnMove(env.gameState, player1.agent, 1)
                else:
                    p1Move, value, _, _ = nnMove(env.gameState, player1.agent, 0)
                board.push(p1Move)

            env.gameState.get_board(board)

            if board.is_game_over():
                break

        gec = get_game_ending_condition(board)

        if gec.count("checkmates") > 0:
            #p1 is white. board.turn needs to be False if p1 win.
            if p1Start:
                if board.turn:
                    p1score[2] += 1
                else:
                    p1score[0] += 1
            #p1 is black. board.turn needs to be True if p1 win.
            else:
                if board.turn:
                    p1score[0] += 1
                else:
                    p1score[2] += 1
        else:
            #draw +1
            p1score[1] += 1
    return p1score


memory = Memory(config.MEMORY_SIZE)
numGame=0
numGames = 5000
numCompeteGames = 20
env = Game()
best_player_version=0

current_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape, env.action_size, config.HIDDEN_CNN_LAYERS)
best_NN = Residual_CNN(config.REG_CONST, config.LEARNING_RATE, env.input_shape, env.action_size, config.HIDDEN_CNN_LAYERS)
#a1 = current agent
a1 = Agent('player1', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, current_NN)
#a2 = best agent
a2 = Agent('player2', env.state_size, env.action_size, config.MCTS_SIMS, config.CPUCT, best_NN)

p1 = Player("nn", nnMove, a1)

p2 = Player("nn", nnMove, a2)

while numGame < numGames:
    train(p1, p2, config.EPISODES)
    numGame += config.EPISODES
    # once enough(?) memory is saved. train the current player, and do the tournament with current vs best.
    # if current is better, update the best one and compete with each other again until # of game is met.
    if len(memory.ltmemory) >= config.MEMORY_SIZE:
        print("training...")
        a1.replay(memory.ltmemory)
        # treat p1 as current player, p2 as best player
        p1score = compete(p1, p2, numCompeteGames)
        numGame += numCompeteGames
        iteration = numGame / config.EPISODES
        if iteration % 1 == 0:
            pickle.dump(memory, open(run_folder + "memory/memory" + str(iteration).zfill(4) + ".p", "wb"))
        # if p1 won more games, p1 is now new best player.
        print("win:", p1score[0], "draw:", p1score[1], "lose:", p1score[2])
        if p1score[0] > p1score[2]:
            best_player_version = best_player_version + 1
            best_NN.model.set_weights(current_NN.model.get_weights())
            best_NN.write(env.name+"best", best_player_version)
            print("updated best one saved")
        else:
            best_player_version = best_player_version + 1
            best_NN.model.set_weights(current_NN.model.get_weights())
            best_NN.write(env.name+"same", best_player_version)
            print("saved the same one.")

    print("Game#", numGame)


print("wow done")


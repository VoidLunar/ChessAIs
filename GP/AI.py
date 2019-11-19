import chess
from Player import Player


# player1 = white piece. moves first    (chess.WHITE (TRUE))
# player2 = black piece                 (chess.BLACK (FALSE))
def play(player1: Player, player2: Player):
    draw = False
    board = chess.Board()

    while True:
        # move white
        possible_moves = get_legal_moves(board.legal_moves)
        p1Move = player1.choose_move(board, possible_moves)
        board.push(p1Move)
        #print(board)
        #print()

        # check if game is over by p1's move
        if board.is_game_over():
            break

        # move black
        possible_moves = get_legal_moves(board.legal_moves)
        p2Move = player2.choose_move(board, possible_moves)
        board.push(p2Move)
        #print(board)
        #print()

        # check if game is over by p2's move
        if board.is_game_over():
            break

    gec = get_game_ending_condition(board)
    return board
    # do something with game ending condition. ( reward winner/ adjust probability etc )


def get_game_ending_condition(board):
    gec = ""
    if board.is_checkmate():
        if board.turn:
            gec = "Black checkmates White"
        else:
            gec = "White checkmates Black"
        pass
    elif board.is_stalemate():
        gec = "Stalemate"
        pass
    elif board.is_insufficient_material():
        gec = "Insufficient pieces to end the game"
        pass
    elif board.is_fivefold_repetition():
        gec = "five fold repetition (draw)"
        pass
    elif board.is_seventyfive_moves():
        gec = "seventy five move rule (draw)"
    return gec


def get_legal_moves(legal_moves):
    moves = []
    for move in legal_moves:
        moves.append(move)
    return moves


def run():
    p1 = Player(input("Input player 1 controller: "))
    p2 = Player(input("Input player 2 controller: "))
    endBoard = (play(p1, p2))
    print(get_game_ending_condition(endBoard))


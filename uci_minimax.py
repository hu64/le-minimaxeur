#!/usr/bin/env python3
import sys
import chess
import chess.engine

# Material evaluation function
def evaluate_board(board):
    """Evaluate the board based on material."""
    if board.is_checkmate():
        # If the current player is in checkmate, it's a loss (-inf)
        return -float('inf') if board.turn else float('inf')
    if board.is_stalemate() or board.is_insufficient_material():
        # Stalemate or insufficient material is a draw (0)
        return 0

    # Material values for each piece type
    material_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }

    # Calculate material score
    score = 0
    for piece_type in material_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * material_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * material_values[piece_type]

    return score

# Minimax algorithm
def minimax(board, depth, maximizing_player):
    """Minimax algorithm with fixed depth."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

# Find the best move using Minimax
def find_best_move(board, depth):
    """Find the best move for the current player."""
    best_move = None
    best_value = -float('inf') if board.turn else float('inf')

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, not board.turn)
        board.pop()

        if board.turn:  # Maximizing player
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:  # Minimizing player
            if board_value < best_value:
                best_value = board_value
                best_move = move

    return best_move

# UCI-compatible engine
def main():
    board = chess.Board()
    depth = 4

    while True:
        line = sys.stdin.readline().strip()
        if line == "uci":
            print("id name Le Minimaxeur")
            print("id author Hughes Perreault")
            print("uciok")
            sys.stdout.flush()
        elif line == "isready":
            print("readyok")
            sys.stdout.flush()
        elif line.startswith("position"):
            tokens = line.split()
            if "startpos" in tokens:
                board.reset()
                if "moves" in tokens:
                    moves_index = tokens.index("moves") + 1
                    for move_str in tokens[moves_index:]:
                        board.push_uci(move_str)
        elif line.startswith("go"):
            tokens = line.split()
            if "depth" in tokens:
                depth_index = tokens.index("depth") + 1
                depth = int(tokens[depth_index])

            best_move = find_best_move(board, depth)
            print(f"bestmove {best_move.uci()}")
            sys.stdout.flush()
        elif line == "ucinewgame":
            board.reset()
        elif line == "quit":
            break

if __name__ == "__main__":
    main()
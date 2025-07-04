#!/usr/bin/env python3
import sys
import chess
import chess.engine
import time
import logging
logging.basicConfig(level=logging.DEBUG)


# Material evaluation function
def evaluate_board(board):
    """Evaluate the board position."""
    if board.is_checkmate():
        return -float('inf') if board.turn else float('inf')

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    # Material values
    material_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
    }

    # Development bonus
    development_bonus = 10

    # Calculate material score
    score = 0
    for piece_type in material_values:
        # logging.debug(f"There are {len(board.pieces(piece_type, chess.WHITE))} {chess.PIECE_NAMES[piece_type]} for White and {len(board.pieces(piece_type, chess.BLACK))} for Black")
        score += len(board.pieces(piece_type, chess.WHITE)) * material_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * material_values[piece_type]

    # # Add development bonus for White
    # for square in board.pieces(chess.KNIGHT, chess.WHITE) | board.pieces(chess.BISHOP, chess.WHITE) | board.pieces(chess.ROOK, chess.WHITE) | board.pieces(chess.QUEEN, chess.WHITE):
    #     if square not in {chess.B1, chess.G1, chess.C1, chess.F1, chess.A1, chess.H1, chess.D1, chess.E1}:  # Starting squares for White
    #         score += development_bonus

    # # Add development bonus for Black
    # for square in board.pieces(chess.KNIGHT, chess.BLACK) | board.pieces(chess.BISHOP, chess.BLACK) | board.pieces(chess.ROOK, chess.BLACK) | board.pieces(chess.QUEEN, chess.BLACK):
    #     if square not in {chess.B8, chess.G8, chess.C8, chess.F8, chess.A8, chess.H8, chess.D8, chess.E8}:  # Starting squares for Black
    #         score -= development_bonus

    # # Encourage moves that increase mobility
    # mobility_bonus = len(list(board.legal_moves)) * 5
    # score += mobility_bonus if board.turn else -mobility_bonus

    # Penalize threefold repetition
    if board.is_repetition():
        score -= 50 if board.turn else -50  # Penalize repetition heavily
        
    return score

# Order moves based on a heuristic
def order_moves(board):
    """Order moves to improve Alpha-Beta Pruning efficiency."""
    def move_score(move):
        # Prioritize captures of higher-value pieces
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            capturing_piece = board.piece_at(move.from_square)
            captured_value = piece_value(captured_piece) if captured_piece else 0
            capturing_value = piece_value(capturing_piece) if capturing_piece else 0
            return 100 + captured_value - capturing_value

        # Prioritize castling
        if board.is_castling(move):
            return 90  # High score for castling moves

        # Prioritize checks
        board.push(move)
        is_check = board.is_check()
        board.pop()
        if is_check:
            return 70  # High score for moves that give check

        # Avoid threefold repetition
        board.push(move)
        is_repetition = board.is_repetition()
        board.pop()
        if is_repetition:
            return -100  # Penalize moves that lead to threefold repetition

        # Prioritize promotions
        if move.promotion:
            return 60  # High score for pawn promotions

        return 0  # Default score for other moves

    def piece_value(piece):
        """Assign a value to each piece type."""
        if piece is None:
            return 0
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King is not captured
        }
        return values.get(piece.piece_type, 0)

    # Sort moves by their heuristic score in descending order
    return sorted(board.legal_moves, key=move_score, reverse=True)

def quiescence_search(board, alpha, beta, start_time, time_limit):
    """Perform quiescence search to evaluate tactical positions."""
    # Check if time limit is exceeded
    if time.time() - start_time > time_limit:
        return evaluate_board(board)

    stand_pat = evaluate_board(board)

    # Alpha-beta pruning
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Consider only captures and checks
    for move in board.legal_moves:
        # Check time limit before processing each move
        if time.time() - start_time > time_limit:
            break

        if board.is_capture(move) or board.gives_check(move):
            board.push(move)
            score = -quiescence_search(board, -beta, -alpha, start_time, time_limit)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha


def minimax(board, depth, alpha, beta, maximizing_player, start_time, time_limit):
    """Minimax algorithm with Alpha-Beta Pruning."""
    if time.time() - start_time > time_limit:
        return evaluate_board(board)

    # if depth == 0 or board.is_game_over():
    #     return quiescence_search(board, alpha, beta, start_time, time_limit)

    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    best_move = None

    if maximizing_player:
        max_eval = -float('inf')
        for move in order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, start_time, time_limit)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, start_time, time_limit)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

        
def find_best_move(board, depth, total_time_remaining):
    """Find the best move for the current player using Alpha-Beta Pruning with Time Management."""
    PLAYING_WHITE = board.turn
    print(f"info string Finding best move for {'White' if PLAYING_WHITE else 'Black'} at depth {depth} with total time remaining {total_time_remaining:.2f} seconds")
    best_move = None
    best_value = -float('inf') if PLAYING_WHITE else float('inf')
    alpha = -float('inf')
    beta = float('inf')

    # Calculate the time limit for this move
    time_limit = total_time_remaining / 25
    start_time = time.time()  # Record the start time

    for move in order_moves(board):
        board.push(move)
        move_value = minimax(board, depth - 1, alpha, beta, not PLAYING_WHITE, start_time, time_limit)
        board.pop()

        # Update the best move
        if PLAYING_WHITE:
            if move_value > best_value:
                best_value = move_value
                best_move = move
            alpha = max(alpha, move_value)
        else:
            if move_value < best_value:
                best_value = move_value
                best_move = move
            beta = min(beta, move_value)

        # Stop searching if time is up
        if time.time() - start_time > time_limit:
            break

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
            total_time_remaining = 50  # Default total time in seconds

            if "depth" in tokens:
                depth_index = tokens.index("depth") + 1
                depth = int(tokens[depth_index])
            if "wtime" in tokens and board.turn:  # White's time remaining
                time_index = tokens.index("wtime") + 1
                total_time_remaining = int(tokens[time_index]) / 1000  # Convert milliseconds to seconds
            if "btime" in tokens and not board.turn:  # Black's time remaining
                time_index = tokens.index("btime") + 1
                total_time_remaining = int(tokens[time_index]) / 1000  # Convert milliseconds to seconds

            best_move = find_best_move(board, depth, total_time_remaining)
            if best_move is not None:
                print(f"bestmove {best_move.uci()}")
            else:
                print("bestmove 0000")  # Indicate no legal moves
            sys.stdout.flush()
        elif line == "quit":
            break

        else:
            print(f"info string Unknown command: {line}")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
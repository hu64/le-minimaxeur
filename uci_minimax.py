#!/usr/bin/env python3
import sys
import chess
import chess.engine
import time
import logging
logging.basicConfig(level=logging.DEBUG)
import chess.polyglot

# Material values
MATERIAL_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 60000  
}
# Transform the piece-square tables into 2D arrays (8x8)
pst_2d = {
    chess.PAWN: [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [78, 83, 86, 73, 102, 82, 85, 90],
        [7, 29, 21, 44, 40, 31, 44, 7],
        [-17, 16, -2, 15, 14, 0, 15, -13],
        [-26, 3, 10, 9, 6, 1, 0, -23],
        [-22, 9, 5, -11, -10, -2, 3, -19],
        [-31, 8, -7, -37, -36, -14, 3, -31],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    chess.KNIGHT: [
        [-66, -53, -75, -75, -10, -55, -58, -70],
        [-3, -6, 100, -36, 4, 62, -4, -14],
        [10, 67, 1, 74, 73, 27, 62, -2],
        [24, 24, 45, 37, 33, 41, 25, 17],
        [-1, 5, 31, 21, 22, 35, 2, 0],
        [-18, 10, 13, 22, 18, 15, 11, -14],
        [-23, -15, 2, 0, 2, 0, -23, -20],
        [-74, -23, -26, -24, -19, -35, -22, -69],
    ],
    chess.BISHOP: [
        [-59, -78, -82, -76, -23, -107, -37, -50],
        [-11, 20, 35, -42, -39, 31, 2, -22],
        [-9, 39, -32, 41, 52, -10, 28, -14],
        [25, 17, 20, 34, 26, 25, 15, 10],
        [13, 10, 17, 23, 17, 16, 0, 7],
        [14, 25, 24, 15, 8, 25, 20, 15],
        [19, 20, 11, 6, 7, 6, 20, 16],
        [-7, 2, -15, -12, -14, -15, -10, -10],
    ],
    chess.ROOK: [
        [35, 29, 33, 4, 37, 33, 56, 50],
        [55, 29, 56, 67, 55, 62, 34, 60],
        [19, 35, 28, 33, 45, 27, 25, 15],
        [0, 5, 16, 13, 18, -4, -9, -6],
        [-28, -35, -16, -21, -13, -29, -46, -30],
        [-42, -28, -42, -25, -25, -35, -26, -46],
        [-53, -38, -31, -26, -29, -43, -44, -53],
        [-30, -24, -18, 5, -2, -18, -31, -32],
    ],
    chess.QUEEN: [
        [6, 1, -8, -104, 69, 24, 88, 26],
        [14, 32, 60, -10, 20, 76, 57, 24],
        [-2, 43, 32, 60, 72, 63, 43, 2],
        [1, -16, 22, 17, 25, 20, -13, -6],
        [-14, -15, -2, -5, -1, -10, -20, -22],
        [-30, -6, -13, -11, -16, -11, -16, -27],
        [-36, -18, 0, -19, -15, -15, -21, -38],
        [-39, -30, -31, -13, -31, -36, -34, -42],
    ],
    chess.KING: [
        [4, 54, 47, -99, -99, 60, 83, -62],
        [-32, 10, 55, 56, 56, 55, 10, 3],
        [-62, 12, -57, 44, -67, 28, 37, -31],
        [-55, 50, 11, -4, -19, 13, 0, -49],
        [-55, -43, -52, -28, -51, -47, -8, -50],
        [-47, -42, -43, -79, -64, -32, -29, -32],
        [-4, 3, -14, -50, -57, -18, 13, 4],
        [17, 30, -3, -14, 6, -1, 40, 18],
    ],
}

ZOBRIST_TABLE = {}

# Material evaluation function
def evaluate_board(board):

    # if chess.polyglot.zobrist_hash(board) in ZOBRIST_TABLE:
    #     return ZOBRIST_TABLE[chess.polyglot.zobrist_hash(board)]

    """Evaluate the board position."""
    if board.is_checkmate():
        score = -float('inf') if board.turn else float('inf')
        ZOBRIST_TABLE[chess.polyglot.zobrist_hash(board)] = score
        return score

    if board.is_stalemate() or board.is_insufficient_material():
        score = 0
        ZOBRIST_TABLE[chess.polyglot.zobrist_hash(board)] = score
        return score

    # Calculate material score
    score = 0
    # for piece_type in MATERIAL_VALUES:
    #     # logging.debug(f"There are {len(board.pieces(piece_type, chess.WHITE))} {chess.PIECE_NAMES[piece_type]} for White and {len(board.pieces(piece_type, chess.BLACK))} for Black")
    #     score += len(board.pieces(piece_type, chess.WHITE)) * MATERIAL_VALUES[piece_type]
    #     score -= len(board.pieces(piece_type, chess.BLACK)) * MATERIAL_VALUES[piece_type]

        # Add material values and piece-square table values
    for piece_type in MATERIAL_VALUES:
        # White pieces
        for square in board.pieces(piece_type, chess.WHITE):
            rank = 7-chess.square_rank(square)
            file = chess.square_file(square)
            score += MATERIAL_VALUES[piece_type] + pst_2d[piece_type][rank][file]

        # Black pieces (reverse the board for Black)
        for square in board.pieces(piece_type, chess.BLACK):
            rank = chess.square_rank(square)  # Reverse rank for Black
            file = chess.square_file(square)  # File remains the same
            score -= MATERIAL_VALUES[piece_type] + pst_2d[piece_type][rank][file]


    mobility_score = 10 * len(list(board.legal_moves))
    score += mobility_score if board.turn else -mobility_score

    nbr_doubled_pawns = count_doubled_pawns(board, chess.WHITE) - count_doubled_pawns(board, chess.BLACK)
    nbr_isolated_pawns = count_isolated_pawns(board, chess.WHITE) - count_isolated_pawns(board, chess.BLACK)
    nbr_blocked_pawns = count_blocked_pawns(board, chess.WHITE) - count_blocked_pawns(board, chess.BLACK)
    DSI = 50 * (nbr_doubled_pawns + nbr_isolated_pawns + nbr_blocked_pawns)
    score += DSI

    ZOBRIST_TABLE[chess.polyglot.zobrist_hash(board)] = score
    return score

def count_doubled_pawns(board, color):
    """Count doubled pawns for a given color."""
    pawns = board.pieces(chess.PAWN, color)
    files = set()
    doubled_count = 0
    for square in pawns:
        file_index = chess.square_file(square)
        if file_index in files:
            doubled_count += 1
        else:
            files.add(file_index)
    return doubled_count

def count_isolated_pawns(board, color):
    """Count isolated pawns for a given color."""
    pawns = board.pieces(chess.PAWN, color)
    isolated_count = 0
    for square in pawns:
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)

        # Check if there are no pawns on adjacent files
        left_file = file_index - 1
        right_file = file_index + 1

        has_left_pawn = left_file >= 0 and any(
            chess.square(left_file, rank) in pawns for rank in range(8)
        )
        has_right_pawn = right_file <= 7 and any(
            chess.square(right_file, rank) in pawns for rank in range(8)
        )

        if not (has_left_pawn or has_right_pawn):
            isolated_count += 1

    return isolated_count

def count_blocked_pawns(board, color):
    """Count blocked pawns for a given color."""
    pawns = board.pieces(chess.PAWN, color)
    blocked_count = 0
    for square in pawns:
        # Check if the pawn is blocked by a piece in front of it
        if color == chess.WHITE and board.piece_at(square + 8) is not None:
            blocked_count += 1
        elif color == chess.BLACK and board.piece_at(square - 8) is not None:
            blocked_count += 1
    return blocked_count

# Order moves based on a heuristic
def order_moves(board):
    """Order moves to improve Alpha-Beta Pruning efficiency."""
    def move_score(move):
        # Prioritize captures of higher-value pieces
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            capturing_piece = board.piece_at(move.from_square)
            if captured_piece is None:
                captured_value = 0
            else:
                captured_value = MATERIAL_VALUES.get(captured_piece.piece_type, 0)
            if capturing_piece is None:
                capturing_value = 0
            else:
                capturing_value = MATERIAL_VALUES.get(capturing_piece.piece_type, 0)
            return 100 + ((captured_value - capturing_value)/100)

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

    # Sort moves by their heuristic score in descending order
    return sorted(board.legal_moves, key=move_score, reverse=True)

def minimax(board, depth, alpha, beta, maximizing_player, start_time, time_limit):
    """Minimax algorithm with Alpha-Beta Pruning."""
    if time.time() - start_time > time_limit:
        return evaluate_board(board)

    if depth <= 0 or board.is_game_over():
        # if any(board.is_capture(move) for move in board.legal_moves):
        #     if maximizing_player:
        #         max_eval = -float('inf')
        #         for move in order_moves(board):
        #             if not board.is_capture(move):
        #                 continue
        #             board.push(move)
        #             eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, start_time, time_limit)
        #             board.pop()
        #             if eval > max_eval:
        #                 max_eval = eval
        #                 best_move = move
        #             alpha = max(alpha, eval)
        #             if beta <= alpha:
        #                 break
        #         return max_eval
        #     else:
        #         min_eval = float('inf')
        #         for move in order_moves(board):
        #             if not board.is_capture(move): 
        #                 continue
        #             board.push(move)
        #             eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, start_time, time_limit)
        #             board.pop()
        #             if eval < min_eval:
        #                 min_eval = eval
        #                 best_move = move
        #             beta = min(beta, eval)
        #             if beta <= alpha:
        #                 break
        #         return min_eval
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
        if best_move is None:
            best_move = move
        board.push(move)
        move_value = minimax(board, depth - 1, alpha, beta, not PLAYING_WHITE, start_time, time_limit)
        if board.is_repetition():
            print(f"info string Move {move.uci()} is a repetition, skipping")
            move_value -= 100 if PLAYING_WHITE else 100
        board.pop()

        # Update the best move
        if PLAYING_WHITE:
            # if move.is_repetition():
            #     move_value -= 100
            if move_value > best_value:
                best_value = move_value
                best_move = move
            alpha = max(alpha, move_value)
        else:
            # if move.is_repetition():
            #     move_value += 100
            if move_value < best_value:
                best_value = move_value
                best_move = move
            beta = min(beta, move_value)

        # Stop searching if time is up
        if time.time() - start_time > time_limit:
            break

    return best_move

def find_best_move_iterative(board, max_depth, total_time_remaining):
    """Find the best move using iterative deepening."""
    best_move = None
    for depth in range(1, max_depth + 1):
        print(f"info string Searching at depth {depth}")
        move = find_best_move(board, depth, total_time_remaining)
        if move is not None:
            best_move = move
        else:
            print("info string No legal moves found")
            break
    return best_move

# UCI-compatible engine
def main():
    board = chess.Board()
    depth = 5

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
        elif line == "ucinewgame":
            board.reset()
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

            best_move = find_best_move_iterative(board, depth, total_time_remaining)
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
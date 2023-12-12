def is_valid_move(board, start_pos, end_pos):
    # Check if start_pos and end_pos are within the board boundaries
    if not is_within_board(start_pos) or not is_within_board(end_pos):
        return False

    # Check if the start position is occupied by the player's piece
    if not is_player_piece(board, start_pos):
        return False

    # Check if the end position is empty or occupied by an opponent's piece
    if is_player_piece(board, end_pos):
        return False

    # Check if the move is valid for the specific piece type
    piece_type = get_piece_type(board, start_pos)
    if not is_valid_move_for_piece(piece_type, start_pos, end_pos):
        return False

    return True

def make_move(board, start_pos, end_pos):
    # Check if the move is valid
    if not is_valid_move(board, start_pos, end_pos):
        return False

    # Update the board with the move
    piece = board[start_pos]
    board[start_pos] = None
    board[end_pos] = piece

    return True

def is_game_over(board):
    # Check if any player has won the game
    if is_checkmate(board):
        return True

    # Check if the game is a draw
    if is_draw(board):
        return True

    return False

def is_checkmate(board):
    # Check if the current player is in checkmate
    # Logic to determine checkmate...

    return False

def is_draw(board):
    # Check if the game is a draw
    # Logic to determine draw...

    return False

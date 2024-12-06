import chess
def render_board(board):
    """Renders a chess board as ASCII art"""
    output = []
    output.append("    a b c d e f g h")
    output.append("  +-----------------+")
    
    for rank in range(7, -1, -1):
        rank_output = f" {rank + 1}|"
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank))
            if piece is None:
                square = "."
            else:
                # Unicode chess pieces
                piece_symbols = {
                    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
                    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
                }
                square = piece_symbols.get(piece.symbol(), piece.symbol())
            rank_output += f" {square}"
        rank_output += " |"
        output.append(rank_output)
    
    output.append("  +-----------------+")
    return "\n".join(output)

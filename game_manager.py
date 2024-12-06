import chess
from models import Game, Move
from app import db
import logging

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.active_games = {}

    def get_or_create_game(self, phone):
        if phone in self.active_games:
            return self.active_games[phone]

        # Check for existing game in database
        game = Game.query.filter_by(white_player=phone, status='active').first()
        if not game:
            # Create new game
            chess_board = chess.Board()
            game = Game(
                white_player=phone,
                fen=chess_board.fen(),
                status='active'
            )
            db.session.add(game)
            db.session.commit()
            
            self.active_games[phone] = ChessGame(game.id, chess_board, phone)
        else:
            # Load existing game
            chess_board = chess.Board(game.fen)
            self.active_games[phone] = ChessGame(game.id, chess_board, phone)

        return self.active_games[phone]

    def get_game(self, phone):
        return self.active_games.get(phone)

    def make_move(self, phone, move_text):
        game = self.get_or_create_game(phone)
        try:
            # Parse and validate move
            move = chess.Move.from_uci(move_text)
            if move not in game.board.legal_moves:
                return False, "Illegal move"

            # Make the move
            game.board.push(move)
            
            # Save to database
            db_game = Game.query.get(game.game_id)
            db_game.fen = game.board.fen()
            
            if game.board.is_checkmate():
                db_game.status = 'checkmate'
            elif game.board.is_stalemate():
                db_game.status = 'stalemate'
            
            move_record = Move(
                game_id=game.game_id,
                player_phone=phone,
                move_text=move_text,
                fen_after=game.board.fen()
            )
            
            db.session.add(move_record)
            db.session.commit()

            status_msg = "Move successful"
            if game.board.is_check():
                status_msg += " - Check!"
            if game.board.is_checkmate():
                status_msg += " - Checkmate!"
            if game.board.is_stalemate():
                status_msg += " - Stalemate!"

            return True, status_msg

        except ValueError as e:
            logger.error(f"Invalid move format: {str(e)}")
            return False, "Invalid move format. Use format like 'e2e4'"
        except Exception as e:
            logger.error(f"Error processing move: {str(e)}")
            return False, "Error processing move"

class ChessGame:
    def __init__(self, game_id, board, white_player):
        self.game_id = game_id
        self.board = board
        self.white_player = white_player
        self.status = 'active'
        self.moves = []

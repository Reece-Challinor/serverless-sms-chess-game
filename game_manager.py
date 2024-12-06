import chess
from models import Game, Move
from app import db
import logging

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.active_games = {}

    def get_or_create_game(self, phone):
        # First check if player is already in a game
        if phone in self.active_games:
            return self.active_games[phone]

        # Check for existing game where player is white or black
        game = Game.query.filter(
            ((Game.white_player == phone) | (Game.black_player == phone)) &
            (Game.status == 'active')
        ).first()

        if not game:
            # Look for a game needing a black player
            game = Game.query.filter_by(black_player=None, status='active').first()
            if game and game.white_player != phone:
                # Join as black player
                game.black_player = phone
                db.session.commit()
            else:
                # Create new game as white player
                chess_board = chess.Board()
                game = Game(
                    white_player=phone,
                    fen=chess_board.fen(),
                    status='active'
                )
                db.session.add(game)
                db.session.commit()

        # Create ChessGame instance
        chess_board = chess.Board(game.fen)
        chess_game = ChessGame(game.id, chess_board, game.white_player, game.black_player)
        self.active_games[phone] = chess_game

        # Also store the game under the opponent's phone if they exist
        if game.black_player and game.black_player != phone:
            self.active_games[game.black_player] = chess_game
        elif game.white_player and game.white_player != phone:
            self.active_games[game.white_player] = chess_game

        return chess_game

    def get_game(self, phone):
        return self.active_games.get(phone)

    def make_move(self, phone, move_text):
        game = self.get_or_create_game(phone)
        try:
            # Validate player is part of the game
            if phone not in [game.white_player, game.black_player]:
                return False, "You are not part of this game"
            
            # Validate it's the player's turn
            if not game.is_player_turn(phone):
                return False, "It's not your turn"

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
    def __init__(self, game_id, board, white_player, black_player=None):
        self.game_id = game_id
        self.board = board
        self.white_player = white_player
        self.black_player = black_player
        self.status = 'active'
        self.moves = []
    
    def is_player_turn(self, phone):
        """Check if it's the given player's turn"""
        if phone not in [self.white_player, self.black_player]:
            return False
        # White moves on even moves (including 0), Black on odd
        is_white_turn = len(self.moves) % 2 == 0
        return (is_white_turn and phone == self.white_player) or \
               (not is_white_turn and phone == self.black_player)
    
    def can_join_as_black(self, phone):
        """Check if a player can join as black"""
        return self.black_player is None and phone != self.white_player

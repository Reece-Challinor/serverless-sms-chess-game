from extensions import db
from datetime import datetime

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    white_player = db.Column(db.String(20), nullable=False)
    black_player = db.Column(db.String(20))
    fen = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_phone = db.Column(db.String(20), nullable=False)
    move_text = db.Column(db.String(10), nullable=False)
    fen_after = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

import os
import logging
from flask import Flask, request, jsonify, render_template
from extensions import db
from game_manager import GameManager
from board_renderer import render_board

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "chess_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Initialize game manager
game_manager = GameManager()

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def index():
    return render_template('game.html')

@app.route('/api/move', methods=['POST'])
def make_move():
    try:
        phone = request.form.get('From')
        move = request.form.get('Body', '').strip().lower()
        
        if not phone or not move:
            return jsonify({'error': 'Missing phone number or move'}), 400

        # Process the move
        game = game_manager.get_or_create_game(phone)
        success, message = game_manager.make_move(phone, move)
        
        if not success:
            return jsonify({'error': message}), 400

        # Get the updated board state
        ascii_board = render_board(game.board)
        
        response = {
            'board': ascii_board,
            'message': message,
            'game_status': game.status
        }
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing move: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400

    game = game_manager.get_game(phone)
    if not game:
        return jsonify({'error': 'No active game found'}), 404

    ascii_board = render_board(game.board)
    return jsonify({
        'board': ascii_board,
        'status': game.status,
        'moves': game.moves
    })

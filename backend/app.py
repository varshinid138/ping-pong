from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Game state variables
game_state = {
    "ball": {"x": 300, "y": 200, "dx": 3, "dy": 3},
    "paddles": {
        "player1": {"y": 150},
        "player2": {"y": 150},
    },
    "obstacles": [],
    "scores": {"player1": 0, "player2": 0},
    "misses": {"player1": 0, "player2": 0},
    "game_over": False,
}

# Generate random obstacles at the start
def generate_obstacles():
    obstacles = []
    for _ in range(2):  # Two obstacles
        obstacles.append({
            "x": random.randint(100, 500),
            "y": random.randint(50, 350),
            "size": 30
        })
    return obstacles

game_state["obstacles"] = generate_obstacles()

@app.route("/")
def index():
    return "Ping Pong Backend Server is Running!"

# Handle player paddle movements
@socketio.on("move_paddle")
def move_paddle(data):
    if game_state["game_over"]:
        return

    player = data["player"]
    direction = data["direction"]

    if player in game_state["paddles"]:
        if direction == "up" and game_state["paddles"][player]["y"] > 0:
            game_state["paddles"][player]["y"] -= 10
        elif direction == "down" and game_state["paddles"][player]["y"] < 300:
            game_state["paddles"][player]["y"] += 10

    emit("update_state", game_state, broadcast=True)

# Handle ball and obstacle updates
@socketio.on("update_ball")
def update_ball():
    if game_state["game_over"]:
        return

    ball = game_state["ball"]
    ball["x"] += ball["dx"]
    ball["y"] += ball["dy"]

    # Bounce off top and bottom walls
    if ball["y"] <= 0 or ball["y"] >= 400:
        ball["dy"] *= -1

    # Bounce off paddles
    if (ball["x"] <= 30 and game_state["paddles"]["player1"]["y"] <= ball["y"] <= game_state["paddles"]["player1"]["y"] + 100) or \
       (ball["x"] >= 570 and game_state["paddles"]["player2"]["y"] <= ball["y"] <= game_state["paddles"]["player2"]["y"] + 100):
        ball["dx"] *= -1

    # Ball misses player 1
    if ball["x"] < 0:
        game_state["misses"]["player1"] += 1
        if game_state["misses"]["player1"] >= 5:
            game_state["game_over"] = True
            emit("update_state", game_state, broadcast=True)
            return
        else:
            game_state["scores"]["player2"] += 1
            reset_ball()

    # Ball misses player 2
    elif ball["x"] > 600:
        game_state["misses"]["player2"] += 1
        if game_state["misses"]["player2"] >= 5:
            game_state["game_over"] = True
            emit("update_state", game_state, broadcast=True)
            return
        else:
            game_state["scores"]["player1"] += 1
            reset_ball()

    # Emit updated state
    emit("update_state", game_state, broadcast=True)

# Reset ball to center
def reset_ball():
    game_state["ball"] = {"x": 300, "y": 200, "dx": 3, "dy": 3}

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

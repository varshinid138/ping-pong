const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const socket = io("http://127.0.0.1:5000");

let gameState = {};

socket.on("update_state", (state) => {
    gameState = state;
    drawGame();
    updateScore();
    if (gameState.game_over) {
        alert("Game Over!");
    }
});

document.addEventListener("keydown", (event) => {
    if (gameState.game_over) return;

    if (event.key === "w") {
        socket.emit("move_paddle", { player: "player1", direction: "up" });
    } else if (event.key === "s") {
        socket.emit("move_paddle", { player: "player1", direction: "down" });
    } else if (event.key === "ArrowUp") {
        socket.emit("move_paddle", { player: "player2", direction: "up" });
    } else if (event.key === "ArrowDown") {
        socket.emit("move_paddle", { player: "player2", direction: "down" });
    }
});

function drawGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw paddles
    ctx.fillRect(10, gameState.paddles.player1.y, 10, 100);
    ctx.fillRect(580, gameState.paddles.player2.y, 10, 100);

    // Draw ball
    ctx.beginPath();
    ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI * 2);
    ctx.fill();

    // Draw obstacles
    for (let obstacle of gameState.obstacles) {
        ctx.fillRect(obstacle.x, obstacle.y, obstacle.size, obstacle.size);
    }
}

function updateScore() {
    document.getElementById("player1Score").textContent = `Player 1: ${gameState.scores.player1}`;
    document.getElementById("player2Score").textContent = `Player 2: ${gameState.scores.player2}`;
}

setInterval(() => {
    if (!gameState.game_over) {
        socket.emit("update_ball");
    }
}, 50);

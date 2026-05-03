import numpy as np
from game_logic import *

DEPTH = 4  # PRO LEVEL
cache = {}  # 🧠 transposition table


# =========================
# 🔥 HASH BOARD (CACHE)
# =========================
def hash_board(board):
    return board.tobytes()


# =========================
# 🧠 HEURISTIC PRO 2048
# =========================
def evaluate(board):
    empty = np.sum(board == 0)
    max_tile = np.max(board)

    # 🔥 Snake pattern (QUAN TRỌNG NHẤT)
    snake_weight = np.array([
        [65536, 32768, 16384, 8192],
        [4096,  2048,  1024,  512],
        [256,   128,   64,    32],
        [16,    8,     4,     2]
    ])
    snake_score = np.sum(board * snake_weight)

    # 🔥 corner lock (giữ tile lớn ở góc)
    corners = [board[0][0], board[0][3], board[3][0], board[3][3]]
    corner_penalty = 0 if max_tile in corners else -max_tile * 0.3

    # 🔥 smoothness (giảm rối)
    smooth = 0
    for i in range(4):
        for j in range(3):
            smooth -= abs(board[i][j] - board[i][j+1])
            smooth -= abs(board[j][i] - board[j+1][i])

    # 🔥 monotonicity (giữ hướng tăng/giảm)
    mono = 0
    for row in board:
        mono += np.sum(np.diff(row))
    for col in board.T:
        mono += np.sum(np.diff(col))

    return (
        empty * 200 +
        snake_score * 1.5 +
        smooth +
        mono +
        corner_penalty
    )


# =========================
# 🎮 MOVE LIST
# =========================
def get_moves():
    return {
        "up": move_up,
        "down": move_down,
        "left": move_left,
        "right": move_right
    }


# =========================
# 🧠 EXPECTIMAX PRO
# =========================
def expectimax(board, depth, is_player):
    key = (hash_board(board), depth, is_player)

    if key in cache:
        return cache[key]

    if depth == 0:
        return evaluate(board)

    # ================= PLAYER =================
    if is_player:
        best = -1e18

        for move, func in get_moves().items():
            new_board = func(board.copy())

            if np.array_equal(board, new_board):
                continue

            score = expectimax(new_board, depth - 1, False)
            best = max(best, score)

        cache[key] = best
        return best

    # ================= RANDOM TILE =================
    empty = list(zip(*np.where(board == 0)))
    if not empty:
        return evaluate(board)

    total = 0

    for (x, y) in empty:
        for value, prob in [(2, 0.9), (4, 0.1)]:
            new_board = board.copy()
            new_board[x][y] = value

            total += prob * expectimax(new_board, depth - 1, True)

    res = total / len(empty)
    cache[key] = res
    return res


# =========================
# 🏆 BEST MOVE
# =========================
def best_move(board):
    global cache
    cache = {}  # reset mỗi turn

    best_score = -1e18
    best = None

    for move, func in get_moves().items():
        new_board = func(board.copy())

        if np.array_equal(board, new_board):
            continue

        score = expectimax(new_board, DEPTH, False)

        if score > best_score:
            best_score = score
            best = move

    return best
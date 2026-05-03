import numpy as np
import random


# 🆕 GAME MỚI
def new_game():
    board = np.zeros((4, 4), dtype=int)
    add_tile(board)
    add_tile(board)
    return board


# ➕ THÊM TILE NGẪU NHIÊN
def add_tile(board):
    empty = list(zip(*np.where(board == 0)))
    if empty:
        x, y = random.choice(empty)
        board[x][y] = 2 if random.random() < 0.9 else 4


# 📦 DỒN SỐ SANG TRÁI
def compress(row):
    new_row = row[row != 0]
    new_row = np.pad(new_row, (0, 4 - len(new_row)))
    return new_row


# 🔥 GỘP SỐ
def merge(row):
    for i in range(3):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
    return row


# ⬅️ MOVE LEFT
def move_left(board):
    new_board = []

    for row in board:
        row = compress(row)
        row = merge(row)
        row = compress(row)
        new_board.append(row)

    return np.array(new_board)


# ➡️ MOVE RIGHT
def move_right(board):
    return np.fliplr(move_left(np.fliplr(board)))


# ⬆️ MOVE UP
def move_up(board):
    return np.transpose(move_left(np.transpose(board)))


# ⬇️ MOVE DOWN
def move_down(board):
    return np.transpose(move_right(np.transpose(board)))
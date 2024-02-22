import math
import sys
from mpi4py import MPI
import random
import time
import numpy as np
from utils import *

DEPTH = 7

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

shape = (6,7) #TODO variable input

def evaluate(current, last_mover, last_col, depth):
    if current.game_over(last_col):  # game over?
        if last_mover == CPU:
            return 1  # victory
        else:
            return -1  # defeat

    if depth == 0:
        return 0

    depth -= 1
    new_mover = HUMAN if last_mover == CPU else CPU
    total = 0
    possible_moves = 0

    for col in range(current.columns()):
        if current.is_legal_move(col):
            possible_moves += 1
            current.move(col, new_mover)
            result = evaluate(current, new_mover, col, depth)
            current.undo_move(col)

            if result > -1:
                all_lose = False
            if result != 1:
                all_win = False
            if result == 1 and new_mover == CPU:
                return 1
            if result == -1 and new_mover == HUMAN:
                return -1
            total += result

    if all_win:
        return 1
    if all_lose:
        return -1

    total /= possible_moves
    return total


def minimax(board, depth, maximizing_player):
    # Base case: check if the game is over or depth limit reached
    if board.game_over() or depth == 0:
        return evaluate(board)

    if maximizing_player:
        max_eval = -math.inf  # or -1 ig
        for move in board.possible_moves(board):
            new_board = board.move(board, move)
            eval = board.minimax(new_board, depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = math.inf  # or 1 ig
        for move in board.possible_moves(board):
            new_board = board.move(board, move)
            eval = board.minimax(new_board, depth - 1, True)

            min_eval = min(min_eval, eval)
        return min_eval


def main():
    if len(sys.argv) < 2:
        print("Uporaba: <program> <fajl s trenutnim stanjem> [<dubina>]")
        return

    b = Board()
    depth = 2

    b.load(sys.argv[1])
    if len(sys.argv) > 2:
        depth = int(sys.argv[2])

    random.seed()

    for col in range(b.col_size):
        if b.game_over(col):
            print("Igra zavrsena!")
            return

    print("Dubina:", depth)
    best = -1
    best_col = -1

    for col in range(b.col_size):
        if b.is_legal_move(col):
            if best_col == -1:
                best_col = col

            b.move(col, CPU)
            result = evaluate(b, CPU, col, depth - 1)
            b.undo_move(col)

            if result > best or (result == best and random.randint(0, 1)):
                best = result
                best_col = col

            print("Stupac", col, ", vrijednost:", result)

    depth //= 2

    while best == -1 and depth > 0:
        print("Dubina:", depth)
        best = -1
        best_col = -1

        for col in range(b.columns()):
            if b.is_legal_move(col):
                if best_col == -1:
                    best_col = col

                b.move(col, CPU)
                result = evaluate(b, CPU, col, depth - 1)
                b.undo_move(col)

                if result > best or (result == best and random.randint(0, 1)):
                    best = result
                    best_col = col

                print("Stupac", col, ", vrijednost:", result)

        depth //= 2

    print("Najbolji:", best_col, ", vrijednost:", best)
    b.move(best_col, CPU)
    b.save(sys.argv[1])

    for col in range(b.col_size):
        if b.game_end(col):
            print("Igra zavrsena! (pobjeda racunala)")
            return

# if __name__ == "__main__":
#     main()

if rank == 0:  # master role
    main()
    tasks = []
    task_num = 49
    #TODO prijava workera
    workers = None
    worker = None

    while task_num < 0: #TODO store n send 49 fields to workers
        task = np.array(tasks[task_num])
        comm.Send(task, dest=worker)
    status = MPI.Status()
    while not comm.Iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status):
        pass
    message = np.empty(1, dtype=int)
    comm.Recv(buf=message, source=status.Get_source())
else:  # worker role
    #TODO prijava radnika prvo myb
    while True:
        task_np = np.empty(shape, dtype=int)
        comm.Recv(task_np,source=0,)

        task = task_np.tolist()


# def minimax(board, depth, maximizing_player):
#     # Base case: check if the game is over or depth limit reached
#     if game_over(board) or depth == 0:
#         return evaluate(board)

#     if maximizing_player:
#         max_eval = -math.inf
#         for move in possible_moves(board):
#             new_board = make_move(board, move)
#             eval = minimax(new_board, depth - 1, False)
#             max_eval = max(max_eval, eval)
#         return max_eval
#     else:
#         min_eval = math.inf
#         for move in possible_moves(board):
#             new_board = make_move(board, move)
#             eval = minimax(new_board, depth - 1, True)
#             min_eval = min(min_eval, eval)
#         return min_eval

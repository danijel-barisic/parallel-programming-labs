
EMPTY = 0
CPU = 1
HUMAN = 2

class Board:
    def __init__(self, row_size, col_size):
        self.row_size = row_size
        self.col_size = col_size
        self.board = [[EMPTY] * col_size for _ in range(row_size)]
        self.height = [0] * col_size
        self.last_mover = EMPTY
        self.last_col = -1

    def print_board(self):
        for row in self.board:
            print(row)

    def game_over(self):
        # Check if the game is over (e.g., someone won or it's a draw)
        col = self.last_col
        row = self.row_size - self.height[col]
        if row < 0:
            return False
        player = self.board[row][col]

        # Vertical
        seq = 1
        r = row - 1
        while r >= 0 and self.field[r][col] == player:
            seq += 1
            r -= 1
        if seq > 3:
            return True

        # Horizontal
        seq = 0
        c = col
        while c - 1 >= 0 and self.field[row][c - 1] == player:
            c -= 1
        while c < self.cols and self.field[row][c] == player:
            seq += 1
            c += 1
        if seq > 3:
            return True

        # Diagonal (left to right)
        seq = 0
        r = row
        c = col
        while c - 1 >= 0 and r - 1 >= 0 and self.field[r - 1][c - 1] == player:
            c -= 1
            r -= 1
        while c < self.cols and r < self.rows and self.field[r][c] == player:
            seq += 1
            c += 1
            r += 1
        if seq > 3:
            return True

        # Diagonal (right to left)
        seq = 0
        r = row
        c = col
        while c - 1 >= 0 and r + 1 < self.rows and self.field[r + 1][c - 1] == player:
            c -= 1
            r += 1
        while c < self.cols and r >= 0 and self.field[r][c] == player:
            seq += 1
            c += 1
            r -= 1
        if seq > 3:
            return True

        return False


    def evaluate(self):
        # Evaluate the current state of the board and assign a score
        # 1, -1, 0, formula...
        pass

    def is_legal_move(self, col):
        assert(col < self.col_size)
        if self.board[self.row_size-1][col] != EMPTY:
            return False
        return True

    def possible_moves(self):
        # Get a list of possible moves from the current board state
        moves = []
        for c in range(0,self.col_size):
            if self.is_legal_move(c):
                moves.append(c)
        return moves

    def move(self, col, player): #TODO pri loadu iz fajla odredi visinu stupaca, međuostalim
        # Make a move on the board and return the updated board
        if not self.is_legal_move(col):
            return False
        self.board[self.row_size-self.board.height[col]][col] = player
        self.board.height[col] += 1
        self.last_mover = player
        self.last_col = col
        return True

    def undo_move(self,col):
        assert(col <= self.col_size)
        if self.height[col] == 0:
            return False
        self.board[self.height[col]-1][col] = EMPTY
        self.height[col] -= 1
        return True


    def load():
        pass #TODO

    def save():
        pass

# Example usage
# board = Board(6, 7)
# board.print_board()
# best_score = minimax(board, 3, True)  # Assuming a depth of 3
# print("Best score:", best_score)

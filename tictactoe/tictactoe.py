"""
Tic Tac Toe Player
"""
import math


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x, o = 0, 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == 'X':
                x+=1
            elif board[i][j] == 'O':
                o+=1
    if x <= o:
        return 'X'
    else:
        return 'O'


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    lst = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                lst.add((i,j))
    return lst


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != EMPTY or action[0] not in range(3) or action[1] not in range(3):
        raise ValueError("Invalid action. ")
    else:
        res = eval(repr(board))
        res[action[0]][action[1]] = player(board)
        return res


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def getMax(board):
        minval = -math.inf
        move = None
        if terminal(board):
            return utility(board), move
        for i in actions(board):
            val, act = getMin(result(board, i))
            if val > minval:
                minval = val
                move = i
                if minval == 1:
                    break
        return minval, move
    def getMin(board):
        maxval = math.inf
        move = None
        if terminal(board):
            return utility(board), move
        for i in actions(board):
            val, act = getMax(result(board, i))
            if val < maxval:
                maxval = val
                move = i
                if maxval == -1:
                    break
        return maxval, move
    if terminal(board):
        return None
    else:
        if (1, 1) in actions(board):
            return (1, 1)
        elif player(board) == 'X':
            val, move = getMax(board)
            return move
        elif player(board) == 'O':
            val, move = getMin(board)
            return move




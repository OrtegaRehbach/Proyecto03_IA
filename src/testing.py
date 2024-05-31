# testing.py
import time
from othello_player import OthelloPlayer

def print_board(board):
    print(" ", " ".join(["0", "1", "2", "3", "4", "5", "6", "7"]))
    for i, row in enumerate(board):
        print(i, " ".join(['.' if cell == 0 else 'B' if cell == -1 else 'W' for cell in row]))
    print()
    
def count_pieces(board):
    black_pieces = sum(row.count(-1) for row in board)
    white_pieces = sum(row.count(1) for row in board)
    return black_pieces, white_pieces

def test_ai_move():
    # Create an instance of the OthelloPlayer with a dummy username
    player = OthelloPlayer('test_player')
    player.current_symbol = -1
    
    # Define different board states to test
    test_boards = [
        # Initial game state
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, -1, 0, 0, 0],
            [0, 0, 0, -1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        # Early game
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0, 0, 0, 0],
            [0, 0, 0, -1, -1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, -1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        # A mid-game state 1
        [
            [1, -1, -1, -1, -1, -1, -1, -1],
            [1, 1, 1, 1, 1, 1, 1, -1],
            [1, 1, 1, 1, 1, 1, -1, -1],
            [1, 1, 1, 1, 1, -1, 0, 0],
            [1, 1, 1, 1, -1, 0, 0, 0],
            [1, 1, 1, -1, 0, 0, 0, 0],
            [1, 1, -1, 0, 0, 0, 0, 0],
            [1, -1, 0, 0, 0, 0, 0, 0]
        ],
        # A mid-game state 2
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 0, 0, 0],
            [0, 1, -1, -1, 1, 0, 0, 0],
            [0, 1, -1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, -1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        # A late-game state 1
        [
            [1, -1, -1, -1, -1, -1, -1, -1],
            [1, 1, 1, 1, 1, 1, 1, -1],
            [1, 1, 1, 1, 1, 1, -1, -1],
            [1, 0, 0, 1, 1, -1, -1, -1],
            [1, 0, 0, 1, -1, -1, -1, -1],
            [1, 0, 1, -1, -1, 0, 0, -1],
            [1, 1, -1, -1, -1, 0, 0, -1],
            [1, -1, -1, -1, -1, 0, -1, -1]
        ],
        # A late-game state 2
        [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, -1, 1, -1, 0, 0],
            [1, 1, 1, 1, -1, -1, 0, 0],
            [1, -1, -1, 1, 0, 0, 0, 0],
            [1, -1, 1, 0, 0, 0, 0, 0]
        ],
        # End-game state
        [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, -1]
        ],
        
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, -1, 0, 0, 0, 0],
            [0, 0, -1, -1, 1, 1, 0, 0],
            [0, 0, -1, 1, 1, 0, 0, 0],
            [0, 0, 1, -1, -1, 0, 0, 0],
            [0, 1, -1, -1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0]
        ]
    ]
    
    for i, board in enumerate(test_boards):
        print(f"Testing board {i+1}")
        print_board(board)
        black_pieces, white_pieces = count_pieces(board)
        print(f"Black pieces: {black_pieces}, White pieces: {white_pieces}")
        start_time = time.time()
        move = player.AI_MOVE(board)
        end_time = time.time()
        print(f"Selected move: {move}")
        print(f"Time taken: {end_time - start_time:.4f} seconds\n")
    
if __name__ == "__main__":
    test_ai_move()

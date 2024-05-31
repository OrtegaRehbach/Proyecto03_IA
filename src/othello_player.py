import requests
import random
import sys
import time

### Public IP Server
### Testing Server
host_name = 'http://192.168.168.241:8000'

class OthelloPlayer():

    def __init__(self, username):
        ### Player username
        self.username = username
        ### Player symbol in a match
        self.current_symbol = 0

    def connect(self, session_name) -> bool:
        new_player = requests.post(host_name + '/player/new_player?session_name=' + session_name + '&player_name=' +self.username)
        new_player = new_player.json()
        self.session_name = session_name
        print(new_player['message'])
        return new_player['status'] == 200

    def play(self) -> bool:
        session_info = requests.post(host_name + '/game/game_info?session_name=' + self.session_name)
        session_info = session_info.json()

        while session_info['session_status'] == 'active':
            try:
                if (session_info['round_status'] == 'ready'):

                    match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                    match_info = match_info.json()

                    while match_info['match_status'] == 'bench':
                        print('You are benched this round. Take a rest while you wait.')
                        time.sleep(15)
                        match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                        match_info = match_info.json()

                    if (match_info['match_status'] == 'active'):
                        self.current_symbol = match_info['symbol']
                        if self.current_symbol == 1:
                            print('Lets play! You are the white pieces.')
                        if self.current_symbol == -1:
                            print('Lets play! You are the black pieces.')

                    while (match_info['match_status'] == 'active'):
                        turn_info = requests.post(host_name + '/player/turn_to_move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +match_info['match'])
                        turn_info = turn_info.json()
                        while not turn_info['game_over']:
                            if turn_info['turn']:
                                print('SCORE ', turn_info['score'])
                                print('Current Board:')
                                self.print_board(turn_info['board'])
                                move = self.AI_MOVE(turn_info['board'])
                                if move is not None:
                                    row, col = move
                                    move_response = requests.post(
                                        host_name + '/player/move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +
                                        match_info['match'] + '&row=' + str(row) + '&col=' + str(col))
                                    move_response = move_response.json()
                                    print(move_response['message'])
                                else:
                                    print("No valid moves available.")
                                    break
                            else:
                                print("Opponent's turn.")
                                opponent_move = self.random_move(turn_info['board'], -self.current_symbol)
                                if opponent_move is not None:
                                    row, col = opponent_move
                                    move_response = requests.post(
                                        host_name + '/player/move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +
                                        match_info['match'] + '&row=' + str(row) + '&col=' + str(col))
                                    move_response = move_response.json()
                                    print(move_response['message'])
                                else:
                                    print("Opponent has no valid moves.")
                                    break
                            time.sleep(2)
                            turn_info = requests.post(host_name + '/player/turn_to_move?session_name=' + self.session_name + '&player_name=' + self.username + '&match_id=' +match_info['match'])
                            turn_info = turn_info.json()

                        if 'winner' in turn_info:
                            print('Game Over. Winner : ' + turn_info['winner'])
                        else:
                            print('Game Over.')
                        
                        match_info = requests.post(host_name + '/player/match_info?session_name=' + self.session_name + '&player_name=' + self.username)
                        match_info = match_info.json()

                else:
                    print('Waiting for match lottery...')
                    time.sleep(5)

            except requests.exceptions.ConnectionError:
                continue

            session_info = requests.post(host_name + '/game/game_info?session_name=' + self.session_name)
            session_info = session_info.json()

    def order_moves(self, moves, board, symbol):
        scored_moves = []
        for move in moves:
            new_board = self.make_move(board, move, symbol)
            score = self.evaluate_board(new_board, symbol)
            scored_moves.append((score, move))
        scored_moves.sort(reverse=True)
        return [move for _, move in scored_moves]

    ### Modify only this function for your AI
    def AI_MOVE(self, board):
        best_move = None
        best_value = float('-inf')
        depth = 4
        moves = self.get_valid_moves(board, self.current_symbol)
        ordered_moves = self.order_moves(moves, board, self.current_symbol)  # Ordenar movimientos para mejorar alpha-beta pruning
        
        for move in ordered_moves:
            new_board = self.make_move(board, move, self.current_symbol)
            move_value = self.minimax(new_board, depth, float('-inf'), float('inf'), False)
            if move_value > best_value:
                best_value = move_value
                best_move = move

        return best_move

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or self.is_terminal(board):
            return self.evaluate_board(board, self.current_symbol)

        if maximizingPlayer:
            maxEval = float('-inf')
            for child in self.get_children(board, self.current_symbol):
                eval = self.minimax(child, depth - 1, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = float('inf')
            for child in self.get_children(board, -self.current_symbol):
                eval = self.minimax(child, depth - 1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return minEval

    def is_stable(self, board, row, col, symbol):
        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        stable = True
        
        for dr, dc in directions:
            r, c = row, col
            while self.is_on_board(r + dr, c + dc):
                r += dr
                c += dc
                if board[r][c] == -symbol:
                    stable = False
                    break
            if not stable:
                break
        
        return stable

    def count_stable_pieces(self, board, symbol):
        stable_count = 0
        for row in range(8):
            for col in range(8):
                if board[row][col] == symbol and self.is_stable(board, row, col, symbol):
                    stable_count += 1
        return stable_count

    def empty_cells_percentage(self, board):
        empty_cells = sum(row.count(0) for row in board)
        total_cells = 64  # 8x8 board
        return (empty_cells / total_cells) * 100

    def evaluate_board(self, board, symbol):
        score = 0
        corners = [(0,0), (0,7), (7,0), (7,7)]
        
        # Calcula el porcentaje de casillas vacías
        empty_percentage = self.empty_cells_percentage(board)
        
        # Control de Esquinas
        for corner in corners:
            if board[corner[0]][corner[1]] == symbol:
                score += 100
            elif board[corner[0]][corner[1]] == -symbol:
                score -= 100
        
        # Solo usa las demás heurísticas si hay menos del 60% de casillas vacías
        if empty_percentage < 60:
            # Movilidad
            my_moves = len(self.get_valid_moves(board, symbol))
            opponent_moves = len(self.get_valid_moves(board, -symbol))
            score += (my_moves - opponent_moves) * 10

            # Estabilidad
            stable_pieces = self.count_stable_pieces(board, symbol)
            score += stable_pieces * 5
        
        return score

    def get_valid_moves(self, board, symbol):
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(board, row, col, symbol):
                    valid_moves.append((row, col))
        return valid_moves

    def is_valid_move(self, board, row, col, symbol):
        if board[row][col] != 0:
            return False
        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if self.is_on_board(r, c) and board[r][c] == -symbol:
                while self.is_on_board(r, c) and board[r][c] == -symbol:
                    r += dr
                    c += dc
                if self.is_on_board(r, c) and board[r][c] == symbol:
                    return True
        return False

    def make_move(self, board, move, symbol):
        board = [row[:] for row in board]
        row, col = move
        board[row][col] = symbol
        directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if self.is_on_board(r, c) and board[r][c] == -symbol:
                flips = []
                while self.is_on_board(r, c) and board[r][c] == -symbol:
                    flips.append((r, c))
                    r += dr
                    c += dc
                if self.is_on_board(r, c) and board[r][c] == symbol:
                    for flip in flips:
                        board[flip[0]][flip[1]] = symbol
        return board

    def get_children(self, board, symbol):
        children = []
        for move in self.get_valid_moves(board, symbol):
            new_board = self.make_move(board, move, symbol)
            children.append(new_board)
        return children

    def is_terminal(self, board):
        return not self.get_valid_moves(board, 1) and not self.get_valid_moves(board, -1)

    def is_on_board(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def print_board(self, board):
        for row in board:
            print(' '.join(['.' if cell == 0 else 'B' if cell == -1 else 'W' for cell in row]))
        print()

if __name__ == '__main__':
    script_name = sys.argv[0]
    ### The first argument is the session id you want to join
    session_id = sys.argv[1]
    ### The second argument is the username you want to have
    player_id = sys.argv[2]

    print('Bienvenido ' + player_id + '!')
    othello_player = OthelloPlayer(player_id)
    if othello_player.connect(session_id):
        othello_player.play()
    print('Hasta pronto!')

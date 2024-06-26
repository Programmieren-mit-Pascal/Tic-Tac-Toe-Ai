import pygame
pygame.init()

class Game:
    
    CIRCLE = 1
    CROSS = 2
    
    def __init__(self, players_turn):
        self.state = [[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0]]
        self.players_turn = players_turn
        self.move_count = 0
        
    def make_move(self, row, column):
        piece = Game.CIRCLE if self.players_turn else Game.CROSS
        self.state[row][column] = piece
        self.players_turn = not self.players_turn
        self.move_count += 1
        
    def undo_move(self, row, column):
        self.state[row][column] = 0
        self.players_turn = not self.players_turn
        self.move_count -= 1
        
    def did_someone_win(self):
        for i in range(3):
            # Horizontal
            if self.state[i][0] == self.state[i][1] == self.state[i][2] != 0:
                return True
            # Vertical
            if self.state[0][i] == self.state[1][i] == self.state[2][i] != 0:
                return True     
        
        # Diagonal
        if self.state[0][0] == self.state[1][1] == self.state[2][2] != 0:
            return True
        if self.state[0][2] == self.state[1][1] == self.state[2][0] != 0:
            return True
        
        return False
        
    def is_move_legal(self, row, column):
        return self.state[row][column] == 0
    
    def find_legal_moves(self):
        legal_moves = []
        for row in range(3):
            for column in range(3):
                if self.is_move_legal(row, column):
                    legal_moves.append((row, column))
        return legal_moves
                
    def board_full(self):
        return self.move_count == 9


class GamePainter:
    
    def __init__(self, win_size):
        self.SQUARE_SIZE = win_size // 3
        self.GRID_THICKNESS = win_size // 100
        self.CIRCLE_THICKNESS = win_size // 35
        self.CIRCLE_RADIUS = self.SQUARE_SIZE // 2.4
        self.CROSS_THICKNESS = win_size // 27
        self.CROSS_SIZE = self.SQUARE_SIZE // 3
        
    def draw_grid(self, screen):
        for row in range(3):
            for column in range(3):
                x = column * self.SQUARE_SIZE
                y = row * self.SQUARE_SIZE
                pygame.draw.rect(screen, (0, 0, 0), 
                                 (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE), self.GRID_THICKNESS)
                
    def draw_game_state(self, screen, game_state):
        for row in range(3):
            for column in range(3):
                piece = game_state[row][column]
                if piece == Game.CIRCLE:
                    self.draw_circle(screen, row, column)
                elif piece == Game.CROSS:
                    self.draw_cross(screen, row, column)
                    
    def draw_circle(self, screen, row, column):
        x, y = self.get_square_center_pos(row, column)
        pygame.draw.circle(screen, (0, 0, 255), (x, y), self.CIRCLE_RADIUS, self.CIRCLE_THICKNESS)
        
    def draw_cross(self, screen, row, column):
        x, y = self.get_square_center_pos(row, column)
        left_x = x - self.CROSS_SIZE
        right_x = x + self.CROSS_SIZE
        top_y = y - self.CROSS_SIZE
        bottom_y = y + self.CROSS_SIZE
        pygame.draw.line(screen, (255, 0, 0), (left_x, top_y), (right_x, bottom_y), self.CROSS_THICKNESS)
        pygame.draw.line(screen, (255, 0, 0), (right_x, top_y), (left_x, bottom_y), self.CROSS_THICKNESS)
        
    def get_square_center_pos(self, row, column):
        x = column * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
        y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
        return (x, y)
        
    def mouse_to_grid_pos(self, mouse_x, mouse_y):
        row = mouse_y // self.SQUARE_SIZE
        row = min(row, 2)
        column = mouse_x // self.SQUARE_SIZE
        column = min(column, 2)
        return (row, column)


def make_computer_move(game):
    global best_move, searched_leaf_nodes
    best_move = None
    searched_leaf_nodes = 0
    evaluation = maximize(game, -float("inf"), float("inf"), 0)
    best_row, best_column = best_move
    game.make_move(best_row, best_column)
    print("Evaluation: ", evaluation)
    print("Searched leaf nodes: ", searched_leaf_nodes)
    print()
    # Intercept inputs that happened while the computer was thinking.
    pygame.event.get()

def maximize(game, alpha, beta, depth):
    global best_move, searched_leaf_nodes
    if game.did_someone_win():
        searched_leaf_nodes += 1
        # Minimizing player made the last move and won. Therefore the maximizing player lost.
        # Add move count to the evaluation because late losses are better than early losses.
        return -100 + game.move_count
    if game.board_full():
        searched_leaf_nodes += 1
        # Board is filled but no player won: Draw.
        return 0
    max_value = -float("inf")
    legal_moves = game.find_legal_moves()
    for move_row, move_column in legal_moves:
        game.make_move(move_row, move_column)
        value = minimize(game, alpha, beta, depth+1)
        game.undo_move(move_row, move_column)
        if value > max_value:
            max_value = value
            if depth == 0:
                best_move = (move_row, move_column)
        if value > alpha:
            alpha = value
        if value >= beta:
            break
    return max_value

def minimize(game, alpha, beta, depth):
    global searched_leaf_nodes
    if game.did_someone_win():
        searched_leaf_nodes += 1
        # Maximizing player made the last move and won.
        # Subtract move count from the evaluation because early wins are better than late wins.
        return 100 - game.move_count
    if game.board_full():
        searched_leaf_nodes += 1
        # Board is filled but no player won: Draw.
        return 0
    min_value = float("inf")
    legal_moves = game.find_legal_moves()
    for move_row, move_column in legal_moves:
        game.make_move(move_row, move_column)
        value = maximize(game, alpha, beta, depth+1)
        game.undo_move(move_row, move_column)
        if value < min_value:
            min_value = value
        if value < beta:
            beta = value
        if value <= alpha:
            break
    return min_value


WIN_SIZE = 600

screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))
pygame.display.set_caption("Tic-Tac-Toe")

FPS = 30
clock = pygame.time.Clock()

painter = GamePainter(WIN_SIZE)
game = Game(False)

game_over = False

if not game.players_turn:
    # Draw the board so that the window is not black while the computer is thinking.
    screen.fill((255, 255, 255))
    painter.draw_game_state(screen, game.state)
    painter.draw_grid(screen)
    pygame.display.update()
    
    # Make the first computer move
    make_computer_move(game)

run = True
while run:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                continue
            
            if game_over:
                continue
            
            mouse_x, mouse_y = event.pos
            row, column = painter.mouse_to_grid_pos(mouse_x, mouse_y)
            if not game.is_move_legal(row, column):
                continue
            
            game.make_move(row, column)
            
            if game.did_someone_win():
                print("Player won!")
                game_over = True
                continue
            if game.board_full():
                game_over = True
                print("Draw!")
                continue
            
            make_computer_move(game)
            
            if game.did_someone_win():
                print("Computer won!")
                game_over = True
                continue
            if game.board_full():
                game_over = True
                print("Draw!")
                continue
            
    screen.fill((255, 255, 255))
    
    painter.draw_game_state(screen, game.state)
    painter.draw_grid(screen)
    
    pygame.display.update()
    
pygame.display.quit()

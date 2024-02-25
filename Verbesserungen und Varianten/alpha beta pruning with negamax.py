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
        self.move_history = []
        
    def make_move(self, row, column):
        piece = Game.CIRCLE if self.players_turn else Game.CROSS
        self.state[row][column] = piece
        self.move_history.append((row, column))
        self.players_turn = not self.players_turn
        self.move_count += 1
        
    def undo_move(self):
        last_row, last_column = self.move_history.pop()
        self.state[last_row][last_column] = 0
        self.players_turn = not self.players_turn
        self.move_count -= 1
    
    def is_move_legal(self, row, column):
        return self.state[row][column] == 0
    
    def get_legal_moves(self):
        legal_moves = []
        for row in range(3):
            for column in range(3):
                if self.is_move_legal(row, column):
                    legal_moves.append((row, column))
        return legal_moves
    
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
        
    def board_full(self):
        return self.move_count == 9
    
    def get_state(self):
        return self.state
    
    def is_players_turn(self):
        return self.players_turn
    
    def get_move_count(self):
        return self.move_count
    
        
class GamePainter:
    
    def __init__(self, win_size):
        self.field_size = win_size // 3
        self.grid_thickness = win_size // 100
        self.circle_thickness = win_size // 35
        self.cirlce_radius = self.field_size // 2.4
        self.cross_thickness = win_size // 27
        self.cross_size = self.field_size // 3
        
    def draw_grid(self, screen):
        for row in range(3):
            for column in range(3):
                x = row * self.field_size
                y = column * self.field_size
                pygame.draw.rect(screen, (0, 0, 0), (x, y, self.field_size, self.field_size), self.grid_thickness)    
        
    def draw_game_state(self, screen, game_state):
        self.draw_grid(screen)
        for row in range(3):
            for column in range(3):
                piece = game_state[row][column]
                if piece == Game.CIRCLE:
                    self.draw_circle(screen, row, column)
                elif piece == Game.CROSS:
                    self.draw_cross(screen, row, column)
    
    def draw_circle(self, screen, row, column):
        x, y = self.get_field_center_pos(row, column)
        pygame.draw.circle(screen, (0, 0, 255), (x, y), self.cirlce_radius, self.circle_thickness)
        
    def draw_cross(self, screen, row, column):
        x, y = self.get_field_center_pos(row, column)
        left_x = x - self.cross_size
        right_x = x + self.cross_size
        top_y = y - self.cross_size
        bottom_y = y + self.cross_size
        pygame.draw.line(screen, (255, 0, 0), (left_x, top_y), (right_x, bottom_y), self.cross_thickness)
        pygame.draw.line(screen, (255, 0, 0), (left_x, bottom_y), (right_x, top_y), self.cross_thickness)
    
    def get_field_center_pos(self, row, column):
        x = column * self.field_size + self.field_size // 2
        y = row * self.field_size + self.field_size // 2
        return (x, y)
    
    def mouse_to_grid_pos(self, mouse_x, mouse_y):
        row = mouse_y // self.field_size
        row = min(row, 2)
        column = mouse_x // self.field_size
        column = min(column, 2)
        return (row, column)


def make_computer_move(game):
    global best_move, searched_leaf_nodes
    best_move = None
    searched_leaf_nodes = 0
    evaluation = minimax(game, -float("inf"), float("inf"), 0)
    best_move_row, best_move_column = best_move
    game.make_move(best_move_row, best_move_column)
    print("Evaluation: ", evaluation)
    print("Searched leaf nodes: ", searched_leaf_nodes)
    print()
    # Intercept inputs that happend while the computer was thinking.
    pygame.event.get()


def minimax(game, alpha, beta, depth):
    global best_move, searched_leaf_nodes
    if game.did_someone_win():
        searched_leaf_nodes += 1
        # Current player lost because the other player made the last move.
        # Add move count to the evaluation because late losses are better than early losses.
        return -100 + game.get_move_count()
    if game.board_full():
        searched_leaf_nodes += 1
        # Board is filled but no player won: Draw.
        return 0
    max_value = -float("inf")
    legal_moves = game.get_legal_moves()
    for move_row, move_column in legal_moves:
        game.make_move(move_row, move_column)
        value = -minimax(game, -beta, -alpha, depth+1)
        game.undo_move()
        if value > max_value:
            max_value = value
            if depth == 0:
                best_move = (move_row, move_column)
        if value > alpha:
            alpha = value
        if value >= beta:
            break
    return max_value
        

WIN_SIZE = 801
screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE))

painter = GamePainter(WIN_SIZE)
game = Game(False)

if not game.is_players_turn():
    # Draw the board so that the window is not black while the computer is thinking.
    screen.fill((255, 255, 255))  
    painter.draw_game_state(screen, game.get_state())
    pygame.display.flip()
    
    # Make the first computer move.
    make_computer_move(game)

FPS = 30
clock = pygame.time.Clock()

game_over = False

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
                game_over = True
                print("Player won!")
                continue
            if game.board_full():
                game_over = True
                print("Draw!")
                continue
            
            make_computer_move(game)
            
            if game.did_someone_win():
                game_over = True
                print("Computer won!")
                continue
            if game.board_full():
                game_over = True
                print("Draw!")
                continue
    
    screen.fill((255, 255, 255))
    
    painter.draw_game_state(screen, game.get_state())
    
    pygame.display.update()

pygame.display.quit()
rows = 8
columns = 8
BOARD_SIZE = 8
import pygame
from threading import Thread
import time

pygame.init()

# Board visualization settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 720
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)

current_board = []
current_checked = 0
is_valid = False
game_running = True

def draw_board(screen, board, checked_count, valid):
    screen.fill(WHITE)
    
    # Draw grid
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
    
    # Draw queens
    font = pygame.font.Font(None, 40)
    for row, col in board:
        x = (col - 1) * CELL_SIZE + CELL_SIZE // 2
        y = (row - 1) * CELL_SIZE + CELL_SIZE // 2
        text = font.render("♛", True, BLUE)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
    
    # Draw info at bottom
    info_font = pygame.font.Font(None, 24)
    status_text = "VALID ✓" if valid else "INVALID"
    status_color = GREEN if valid else RED
    info1 = info_font.render(f"Checked: {checked_count} | {status_text}", True, BLACK)
    info2 = info_font.render(f"Queens: {len(board)}/{BOARD_SIZE}", True, BLACK)
    screen.blit(info1, (10, WINDOW_HEIGHT - 40))
    screen.blit(info2, (10, WINDOW_HEIGHT - 20))
    
    pygame.display.flip()

def visualization_loop():
    global game_running
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("8 Queens Problem - Brute Force")
    clock = pygame.time.Clock()
    
    while game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        
        draw_board(screen, current_board, current_checked, is_valid)
        clock.tick(FPS)
    
    pygame.quit()

def under_attack_full(board):
    for i in range(len(board)):
        r1, c1 = board[i]
        for j in range(i + 1, len(board)):
            r2, c2 = board[j]
            if c1 == c2:
                return True
            if abs(r1 - r2) == abs(c1 - c2):
                return True
    return False


def brute_force(visualize=True):
    global current_board, current_checked, is_valid, game_running
    
    solutions = []
    positions_checked = 0
    viz_thread = None
    
    # Start visualization thread
    if visualize:
        viz_thread = Thread(target=visualization_loop, daemon=False)
        viz_thread.start()

    def generate(row, board):
        global current_board, current_checked, is_valid
        nonlocal positions_checked

        if row > BOARD_SIZE:
            positions_checked += 1
            current_checked = positions_checked
            current_board = board[:]
            is_valid = not under_attack_full(board)
            
            # time.sleep(0.001)
            
            if is_valid:
                solutions.append(board[:])
            return

        for column in range(1, BOARD_SIZE + 1):
            board.append((row, column))
            current_board = board[:]
            generate(row + 1, board)
            board.pop()

    generate(1, [])
    
    game_running = False
    
    # Wait for visualization thread to finish
    if viz_thread:
        viz_thread.join(timeout=5)

    info = {
        "valid solutions": len(solutions),
        "queens": BOARD_SIZE,
        "board size": f"{rows}x{columns}",
        "total positions checked": positions_checked,
    }
    print(info)

    return solutions

brute_force(visualize=True)
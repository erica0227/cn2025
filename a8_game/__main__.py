import pygame
import queue
from map import grid

# Constants
GRID_WIDTH = len(grid[0])
GRID_HEIGHT = len(grid)
GRID_SIZE = 30
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Initialize game variables
pacman_pos = [7, 7]
ghost_pos = [1, 1]
ghost_positions = [(1, 1)]
score = 0
game_over = False

# Get Pac-Man & Ghost positions
def get_positions() -> None:
    global pacman_pos, ghost_pos, ghost_positions
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            if cell == 4:
                pacman_pos = [row_idx, col_idx]
            elif cell == 3:
                ghost_pos = [row_idx, col_idx]
                ghost_positions.append([row_idx, col_idx])

def draw_maze(screen, ghost1, pacman) -> None:
    global ghost_pos, ghost_positions
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * GRID_SIZE, row_idx * GRID_SIZE
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            elif cell == 3:
                screen.blit(ghost1, (ghost_pos[1] * GRID_SIZE, ghost_pos[0] * GRID_SIZE))
            elif cell == 4:
                screen.blit(pacman, (pacman_pos[1] * GRID_SIZE, pacman_pos[0] * GRID_SIZE))

def move_ghost(direction, screen) -> None:
    global ghost_pos
    row, col = ghost_pos
    new_row, new_col = row, col
    if direction == "UP":
        new_row -= 1
    elif direction == "DOWN":
        new_row += 1
    elif direction == "LEFT":
        new_col -= 1
    elif direction == "RIGHT":
        new_col += 1

    # if grid[new_row][new_col] != 1:
    grid[row][col] = 0  # Clear old position
    grid[new_row][new_col] = 3  # Move ghost
    ghost_pos = [new_row, new_col]

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
    pygame.display.set_caption("pacman")
    pacman = pygame.image.load('images/pacman.png').convert_alpha()
    ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()

    # Set up BFS queue and visited set
    bfs_queue = queue.Queue()
    visited: set[tuple[int,int]] = set()
    # Better for debugging and tuple is a good practice

    run = True
    while run:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_ghost("UP", screen)
                elif event.key == pygame.K_DOWN:
                    move_ghost("DOWN", screen)
                elif event.key == pygame.K_LEFT:
                    move_ghost("LEFT", screen)
                elif event.key == pygame.K_RIGHT:
                    move_ghost("RIGHT", screen)

        draw_maze(screen, ghost1, pacman)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
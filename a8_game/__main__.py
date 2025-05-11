import pygame
import random
import queue

grid: list[list[int]] = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
GRID_WIDTH = len(grid[0])
GRID_HEIGHT = len(grid)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
CELL_SIZE = 40

# Initialize game variables
enemy = []
pacman_pos = None
ghost_pos = None
# score = 0
# game_over = False

def main() -> None:
    pygame.init()

    # Screen and image
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    # player = pygame.Rect((300, 250, 40, 40))
    pacman = pygame.image.load('images/pac_man.png').convert_alpha()
    ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()
    pygame.display.set_caption("pacman")

    # Initialize game variables
    # score = 0
    # game_over = False

    # Initialize ghost position
    ghost_pos = None
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if grid[i][j] == 3:
                character_pos = (i, j)
                grid[i][j] = 0
                break

    # Set up BFS queue and visited set
    bfs_queue = queue.Queue()
    visited: set[tuple[int,int]] = set()
    # better for debugging and tuple is a good practice

    run = True
    while run:
        screen.fill((0, 0, 0))
        add_pacman()

        # Draw the map
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif grid[y][x] == 0:
                    pygame.draw.circle(screen, YELLOW, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 3)
                elif grid[y][x] == 3:
                    # Draw ghost
                    screen.blit(ghost1, (j * CELL_SIZE, i * CELL_SIZE))
                elif grid[y][x] == 5:
                    # Draw pacman
                    screen.blit(pacman, (j * CELL_SIZE, i * CELL_SIZE))

        # Move the ghost
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            ghost1.move_ip(-1, 0)
        elif key[pygame.K_RIGHT]:
            ghost1.move_ip(1, 0)
        elif key[pygame.K_UP]:
            ghost1.move_ip(0, -1)
        elif key[pygame.K_DOWN]:
            ghost1.move_ip(0, 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()

# Function to check if a position is within the bounds of the grid
def is_valid(pos):
    i, j = pos
    return i >= 0 and i < GRID_HEIGHT and j >= 0 and j < GRID_WIDTH

# Function to check if a position is a boundary
def is_boundary(pos):
    i, j = pos
    return grid[i][j] == 1

# Function to check if a position is an enemy
def is_pacman(pos):
    i, j = pos
    return grid[i][j] == 5

# Function to add an enemy to the grid
def add_pacman():
    pacman_pos = (random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1))
    while grid[pacman_pos[0]][pacman_pos[1]] != 0 or pacman_pos == ghost_pos or pacman_pos in enemy:
        pacman_pos = (random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1))
    grid[pacman_pos[0]][pacman_pos[1]] = 5
    enemy.append(pacman_pos)

if __name__ == "__main__":
    main()
import pygame
import queue
from map import grid

# Constants
GRID_WIDTH = len(grid[0])
GRID_HEIGHT = len(grid)
CELL_SIZE = 40
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Initialize game variables
enemy = []
pacman_pos = None
ghost_pos = None
# score = 0
# game_over = False

def move_pacman(direction, screen) -> None:
    row, col = pacman_pos
    new_row, new_col = row, col
    if direction == "UP":
        new_row -= 1
    elif direction == "DOWN":
        new_row += 1
    elif direction == "LEFT":
        new_col -= 1
    elif direction == "RIGHT":
        new_col += 1

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("pacman")
    pacman = pygame.image.load('images/pacman.png').convert_alpha()
    ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 3:
                ghost_pos = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                break
            if grid[y][x] == 4:
                pacman_pos = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                break

    # Set up BFS queue and visited set
    bfs_queue = queue.Queue()
    visited: set[tuple[int,int]] = set()
    # Better for debugging and tuple is a good practice

    run = True
    while run:
        screen.fill(BLACK)

        # Draw the map
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        screen.blit(ghost1, ghost_pos)
        # pacman_pos = (random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1))
        # enemy.append(pacman_pos)
        screen.blit(pacman, pacman_pos)

        # Move the ghost
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            ghost_pos.move_ip(-1, 0)
        elif key[pygame.K_RIGHT]:
            ghost_pos.move_ip(1, 0)
        elif key[pygame.K_UP]:
            ghost_pos.move_ip(0, -1)
        elif key[pygame.K_DOWN]:
            ghost_pos.move_ip(0, 1)

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         exit()
        #     elif event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_UP:
        #             move_pacman("UP", screen)
        #         elif event.key == pygame.K_DOWN:
        #             move_pacman("DOWN", screen)
        #         elif event.key == pygame.K_LEFT:
        #             move_pacman("LEFT", screen)
        #         elif event.key == pygame.K_RIGHT:
        #             move_pacman("RIGHT", screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
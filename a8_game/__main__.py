import pygame
import queue


from map import grid

# Constants
GRID_WIDTH = len(grid[0])
GRID_HEIGHT = len(grid)
GRID_SIZE = 30
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Initialize game variables
current_direction = None
pacman_pos = (7, 7)
ghost_pos = [1, 1]
ghost_positions = [(1, 1)]
lives = 3
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
                ghost_positions.append((row_idx, col_idx))

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

    if grid[new_row][new_col] != 1:
        grid[row][col] = 0  # Clear old position
        grid[new_row][new_col] = 3  # Move ghost
        ghost_pos = [new_row, new_col]
        move_pacman()

    check_collision(screen)

# The function for moving pacman
def move_pacman() -> None:
    global pacman_pos

    print("Pacman moved")
    print("Pacman position:", pacman_pos)
    direction = bfs_alg()

    print(pacman_pos)
    pacman_pos = tuple_add(pacman_pos, direction)
    print(pacman_pos)

def check_collision(screen):
    global lives, pacman_pos, ghost_pos, ghost_positions, current_direction
    for ghost in ghost_positions:
        if ghost_pos == pacman_pos:
            lives -= 1
            if lives > 0:
                display_message(screen, "You lost a life!", RED)
            if lives == 0:
                display_message(screen, "Game Over!", RED)
                pygame.quit()
                exit()

            # Reset Pac-Man position and update the maze immediately
            old_row, old_col = ghost_pos
            grid[old_row][old_col] = 0  # Clear old position
            ghost_pos = [1, 1]  # Reset to start position
            grid[1][1] = 3  # Place Pac-man back on the grid
            grid[7][7] = 4  # Place Ghost back on the grid
            current_direction = None

def display_message(screen, message, color = WHITE):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)

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

def tuple_add(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]
def inverse_tuple(t1: tuple[int, int]) -> tuple[int, int]:
    return -t1[0], -t1[1]


def bfs_alg():
    global ghost_pos, ghost_positions, pacman_pos
    ghost_set = set()
    for ghost in ghost_positions:
        ghost_set.add(ghost)
    visited = set()
    visited.add(pacman_pos)
    visit_grid = grid.copy()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    q = queue.Queue()
    q.put(pacman_pos)
    counter = 3
    visit_grid[pacman_pos[0]][pacman_pos[1]] = 2
    temp_q = queue.Queue()
    flag = True
    nearest_ghost = None
    while not q.empty() and flag:
        print(counter)
        while not q.empty() and flag:
            pos = q.get()
            for direction in directions:
                next_pos = tuple_add(pos, direction)
                if visit_grid[next_pos[0]][next_pos[1]] == 0:
                    visit_grid[next_pos[0]][next_pos[1]] = counter
                    temp_q.put(next_pos)
                if next_pos in ghost_set:
                    flag = False
                    nearest_ghost = pos
                    break

        del q
        q = temp_q
        temp_q = queue.Queue()
        counter += 1
    counter -= 1
    pacman_reached = False
    last_direction = None
    current_position = nearest_ghost
    while not pacman_reached:
        print(counter)
        counter -= 1
        for direction in directions:
            print("direction", direction)
            print(current_position)
            new_pos = tuple_add(current_position, direction)
            print(new_pos)
            if visit_grid[new_pos[0]][new_pos[1]] == counter:
                last_direction = direction
                current_position = new_pos
                print(current_position)
                if pacman_pos == new_pos:
                    pacman_reached = True
                    return inverse_tuple(last_direction)
                break

def main() -> None:
    global current_direction
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

        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives - 1}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (GRID_WIDTH * GRID_SIZE - 100, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_direction = "UP"
                elif event.key == pygame.K_DOWN:
                    current_direction = "DOWN"
                elif event.key == pygame.K_LEFT:
                    current_direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    current_direction = "RIGHT"

        if current_direction:
            try:
                #move_pacman()
                pass
            except Exception as e:
                run = False
                pygame.quit()
                raise e
            move_ghost(current_direction, screen)
        draw_maze(screen, ghost1, pacman)
        pygame.display.flip()
        clock.tick(2)


if __name__ == "__main__":
    main()
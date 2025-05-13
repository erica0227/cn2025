import socket
import pygame
import queue
import copy
from map2 import grid

# Constants
GRID_WIDTH = len(grid[0])
GRID_HEIGHT = len(grid)
GRID_SIZE = 30
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Initialize game variables
lives = 3
score = 0
game_over = False
current_direction = None
pacman_pos = ()
ghost_pos = ()
ghost_positions = []
for row_idx, row in enumerate(grid):
    for col_idx, cell in enumerate(row):
        if cell == 2:
            pacman_pos = (row_idx, col_idx)
        elif cell == 3:
            ghost_pos = (row_idx, col_idx)
            ghost_positions.append((row_idx, col_idx))
            # print(ghost_positions)

# Get Pac-Man & Ghost positions
def get_positions() -> None:
    global pacman_pos, ghost_pos, ghost_positions
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            if cell == 2:
                pacman_pos = (row_idx, col_idx)
            elif cell == 3:
                ghost_pos = (row_idx, col_idx)
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
        ghost_pos = (new_row, new_col)

    check_collision(screen)
    move_pacman(screen)

# The function for moving pacman
def move_pacman(screen) -> None:
    global pacman_pos

    print("Pacman moved")
    print("Pacman position:", pacman_pos)
    print("ghost position:", ghost_pos)
    direction = bfs_alg()

    print("Pacman position:", pacman_pos)
    pacman_pos = tuple_add(pacman_pos, direction)
    print("Pacman position:", pacman_pos)
    check_collision(screen)

def check_collision(screen):
    global lives, pacman_pos, ghost_pos, ghost_positions, current_direction
    if ghost_pos == pacman_pos:
        lives -= 1
        if lives > 0:
            display_message(screen, "You lost a life!", RED)
        if lives == 0:
            display_message(screen, "Game Over!", RED)
            pygame.quit()
            exit()

        # Reset Pac-Man position and update the maze immediately
        grid[pacman_pos[0]][pacman_pos[1]] = 0
        grid[ghost_pos[0]][ghost_pos[1]] = 0

        # Now reset logical positions
        ghost_pos = (1, 13)
        pacman_pos = (7, 7)

        # Now update grid to show new positions
        grid[ghost_pos[0]][ghost_pos[1]] = 3
        grid[pacman_pos[0]][pacman_pos[1]] = 2
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
            elif cell == 2:
                screen.blit(pacman, (pacman_pos[1] * GRID_SIZE, pacman_pos[0] * GRID_SIZE))

def tuple_add(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]
def inverse_tuple(t1: tuple[int, int]) -> tuple[int, int]:
    return -t1[0], -t1[1]


def bfs_alg():
    global pacman_pos, ghost_pos, ghost_positions
    visit_grid = copy.deepcopy(grid)  # deep copy
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    q = queue.Queue()
    q.put(pacman_pos)
    visited = set()
    visited.add(pacman_pos)
    visit_grid[pacman_pos[0]][pacman_pos[1]] = 2  # mark start
    counter = 3
    ghost_found = False
    ghost_position = None

    while not q.empty() and not ghost_found:
        size = q.qsize()
        for _ in range(size):
            pos = q.get()
            for d in directions:
                next_pos = tuple_add(pos, d)
                r, c = next_pos
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if visit_grid[r][c] == 0 and next_pos not in visited:
                        visit_grid[r][c] = counter
                        visited.add(next_pos)
                        q.put(next_pos)
                    elif (r, c) == tuple(ghost_pos):
                        visit_grid[r][c] = counter
                        ghost_position = (r, c)
                        ghost_found = True
                        break
        counter += 1

    if not ghost_position:
        return (0, 0)  # fallback if no ghost found

    # Backtrack from ghost to Pac-Man
    current = ghost_position
    while True:
        for d in directions:
            prev = tuple_add(current, d)
            r, c = prev
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                if visit_grid[r][c] == visit_grid[current[0]][current[1]] - 1:
                    current = prev
                    if current == pacman_pos:
                        return inverse_tuple(d)
                    break


def main() -> None:
    global current_direction
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
    pygame.display.set_caption("pacman")
    pacman = pygame.image.load('images/pacman.png').convert_alpha()
    ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()

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

# import pygame
# import socket
# import struct
#
# grid: list[list[int]] = [
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#     [1, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
#     [1, 1, 1, 1, 0, 1, 0, 2, 0, 1, 0, 1, 1, 1, 1],
#     [1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
# ]
#
# # Constants
# GRID_WIDTH = len(grid[0])
# GRID_HEIGHT = len(grid)
# GRID_SIZE = 30
# BLACK = (0, 0, 0)
# BLUE = (0, 0, 255)
# RED = (255, 0, 0)
# WHITE = (255, 255, 255)
#
# # Initialize game variables
# current_direction = None
# pacman_pos = [7, 7] # Do we need to use tuple
# ghost_pos = [1, 1]
# ghost_positions = [(1, 1)]
# lives = 3
# score = 0
# game_over = False
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# client1_addr = ("127.0.0.1", 6000)  # Client1 监听端口
#
# def draw_maze(screen, ghost1, pacman) -> None:
#     global ghost_pos, ghost_positions
#     for row_idx, row in enumerate(grid):
#         for col_idx, cell in enumerate(row):
#             x, y = col_idx * GRID_SIZE, row_idx * GRID_SIZE
#             if cell == 1:
#                 pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
#             elif cell == 3:
#                 screen.blit(ghost1, (ghost_pos[1] * GRID_SIZE, ghost_pos[0] * GRID_SIZE))
#             elif cell == 2:
#                 screen.blit(pacman, (pacman_pos[1] * GRID_SIZE, pacman_pos[0] * GRID_SIZE))
#
# def send_position(row, col):
#     packet = struct.pack("!BHH", 2, row, col)  # type=2, row, col
#     sock.sendto(packet, client1_addr)
#
# def main() -> None:
#     pygame.init()
#     screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
#     pygame.display.set_caption("pacman")
#     pacman = pygame.image.load('images/pacman.png').convert_alpha()
#     ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()
#
#     # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # host_port = ("127.0.0.1", 5378)
#     # sock.connect(host_port)
#     # print("Connected to server")
#     # message = "HELLO FROM CLIENT1".encode("utf-8")
#     # while True:
#     #     send_msg(sock, message)
#
#     running = True
#     while running:
#         # 1. get keyboard input
#         # 2. send direction to server
#         # 3. receive state from server
#         # 4. render draw_maze()
#         # 5. tick clock
#         screen.fill(BLACK)
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 exit()
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_UP:
#                     current_direction = "UP"
#                 elif event.key == pygame.K_DOWN:
#                     current_direction = "DOWN"
#                 elif event.key == pygame.K_LEFT:
#                     current_direction = "LEFT"
#                 elif event.key == pygame.K_RIGHT:
#                     current_direction = "RIGHT"
#
#         draw_maze(screen, ghost1, pacman)
#         pygame.display.flip()
#
# if __name__ == "__main__":
#     main()
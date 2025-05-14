import socket
import select
import pygame
import queue
import copy
import struct
from map1 import grid

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
last_direction = None
direction_send = 0
client_id_recv = 0
packet_type_recv = 0
ghost1_direction = None
pacman_pos = ()
ghost1_pos = ()
ghost2_pos = ()
ghost1_start = ()
ghost2_start = ()
ghost_positions = []
for row_idx, row in enumerate(grid):
    for col_idx, cell in enumerate(row):
        if cell == 2:
            pacman_pos = (row_idx, col_idx)
        elif cell == 3:
            ghost1_start = (row_idx, col_idx)
            ghost1_pos = (ghost1_start)
            ghost_positions.append(ghost1_pos)
        elif cell == 4:
            ghost2_start = (row_idx, col_idx)
            ghost2_pos = ghost2_start
            ghost_positions.append(ghost2_pos)
            # print(ghost_positions)

def move_ghost(direction, screen) -> None:
    global ghost1_pos
    row, col = ghost1_pos
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
        ghost1_pos = (new_row, new_col)

    check_collision(screen)
    move_pacman(screen)

def move_pacman(screen) -> None:
    global pacman_pos

    print("Pacman moved")
    print("Pacman position:", pacman_pos)
    # print("ghost position:", ghost1_pos)
    direction = bfs_alg()

    # print("Pacman position:", pacman_pos)
    pacman_pos = tuple_add(pacman_pos, direction)
    # print("Pacman position:", pacman_pos)
    check_collision(screen)

def check_collision(screen):
    global lives, pacman_pos, ghost1_pos, ghost_positions, current_direction
    if ghost1_pos == pacman_pos:
        lives -= 1
        if lives > 0:
            display_message(screen, "You lost a life!", RED)
        if lives == 0:
            display_message(screen, "Game Over!", RED)
            pygame.quit()
            exit()

        # Reset Pac-Man position and update the maze immediately
        grid[pacman_pos[0]][pacman_pos[1]] = 0
        grid[ghost1_pos[0]][ghost1_pos[1]] = 0

        # Now reset logical positions
        ghost1_pos = ghost1_start
        pacman_pos = (7, 7)

        # Now update grid to show new positions
        grid[ghost1_pos[0]][ghost1_pos[1]] = 3
        grid[pacman_pos[0]][pacman_pos[1]] = 2
        current_direction = None
        last_direction = None

def display_message(screen, message, color = WHITE):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)

def draw_maze(screen, ghost1, ghost2, pacman) -> None:
    global ghost1_pos, ghost_positions
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * GRID_SIZE, row_idx * GRID_SIZE
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            elif cell == 2:
                screen.blit(pacman, (pacman_pos[1] * GRID_SIZE, pacman_pos[0] * GRID_SIZE))
            elif cell == 3:
                screen.blit(ghost1, (ghost1_pos[1] * GRID_SIZE, ghost1_pos[0] * GRID_SIZE))
            elif cell == 4:
                screen.blit(ghost2, (ghost2_pos[1] * GRID_SIZE, ghost2_pos[0] * GRID_SIZE))

def tuple_add(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]

def inverse_tuple(t1: tuple[int, int]) -> tuple[int, int]:
    return -t1[0], -t1[1]

def bfs_alg():
    global pacman_pos, ghost1_pos, ghost_positions
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
                    elif (r, c) == tuple(ghost1_pos):
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
    global current_direction, last_direction, direction_send, client_id_recv, packet_type_recv
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
    pygame.display.set_caption("pacman1")
    pacman = pygame.image.load('images/pacman.png').convert_alpha()
    ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()
    ghost2 = pygame.image.load('images/ghost2.png').convert_alpha()

    client1_addr = ("0.0.0.0", 12345)
    client2_addr = ("0.0.0.0", 12346)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(client1_addr)
    client_sockets = [client_socket]

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
            move_ghost(current_direction, screen)

        # Interest management
        if current_direction != last_direction and current_direction != None:
            print("current direction:", current_direction)
            print("last direction:", last_direction)
            if current_direction == "UP":
                direction_send = 1
            elif current_direction == "DOWN":
                direction_send = 2
            elif current_direction == "LEFT":
                direction_send = 3
            elif current_direction == "RIGHT":
                direction_send = 4
            last_direction = current_direction

            # Send direction data
            packet_type_send = 1 # 1 means position
            client_id_send = 2 # send to ghost2
            packet = struct.pack("BBB", client_id_send, packet_type_send, direction_send)
            client_socket.sendto(packet, client2_addr)
            print("sent packet:", packet)

        # Recv direction data
        client_socket.setblocking(False)
        try:
            data, addr = client_socket.recvfrom(1024)
            print(data, "from", addr)
            client_id_recv, packet_type_recv, direction = struct.unpack("BBB", data)
            print("Received:", client_id_recv, packet_type_recv, direction)
        except BlockingIOError:
            pass

        draw_maze(screen, ghost1, ghost2, pacman)
        pygame.display.flip()
        clock.tick(2)

if __name__ == "__main__":
    main()
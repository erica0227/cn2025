import socket
import select
import pygame
import queue
import copy
import struct
import time
from map import grid

# Constants
GRID_WIDTH = len(grid[0])
GRID_HEIGHT = len(grid)
GRID_SIZE = 30
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

current_ghost = 1
ghosts = {
    1: {"pos": (1, 1), "start": (1, 1), "cell": 3, "direction": None, "seq": 0, "skip_frame": False},
    2: {"pos": (1, 13), "start": (1, 13), "cell": 4, "direction": None, "seq": 0, "skip_frame": False},
    3: {"pos": (13, 1), "start": (13, 1), "cell": 5, "direction": None, "seq": 0, "skip_frame": False}
}

# Initialize game variables
lives = 3
score = 0
game_over = False
current_direction = None
last_direction = None
direction_send = 0
client_id_recv = 0
packet_type_recv = 0
pacman_pos = (7, 7)

def move_ghost(ghost_id, direction, screen, clients, server_socket) -> None:
    ghost = ghosts[ghost_id]
    row, col = ghost["pos"]
    new_row, new_col = row, col
    if direction == "UP":
        new_row -= 1
    elif direction == "DOWN":
        new_row += 1
    elif direction == "LEFT":
        new_col -= 1
    elif direction == "RIGHT":
        new_col += 1

    if grid[new_row][new_col] != 1 and grid[new_row][new_col] != 4 and grid[new_row][new_col] != 5:
        grid[row][col] = 0  # Clear old position
        grid[new_row][new_col] = ghost["cell"]  # Move ghost
        ghost["pos"] = (new_row, new_col)

    if ghost_id == current_ghost:
        check_collision(ghost_id, screen, clients, server_socket)
        move_pacman(ghost_id, screen, clients, server_socket)

def move_pacman(ghost_id, screen, clients, server_socket) -> None:
    global pacman_pos

    print("Pacman moved")
    print("Pacman position:", pacman_pos)
    direction = bfs_alg(ghost_id)

    pacman_pos = tuple_add(pacman_pos, direction)
    check_collision(ghost_id, screen, clients, server_socket)

def check_collision(ghost_id, screen, clients, server_socket):
    global lives, pacman_pos, current_direction
    ghost = ghosts[ghost_id]
    if ghost["pos"] == pacman_pos:
        lives -= 1
        if lives > 0:
            packet_type = 3
            ghost_id_send = ghost_id
            seq = ghost["seq"] + 1
            ghost["seq"] = seq
            packet = struct.pack("BBBBB", ghost_id_send, packet_type, 0, 0, seq)
            print("packet", packet)
            for client in clients:
                server_socket.sendto(packet, client)
            display_message(screen, "You lost a life!", RED)
        if lives == 0:
            packet_type = 4
            ghost_id_send = ghost_id
            seq = ghost["seq"] + 1
            ghost["seq"] = seq
            packet = struct.pack("BBBBB", ghost_id_send, packet_type, 0, 0, seq)
            print("packet", packet)
            for client in clients:
                server_socket.sendto(packet, client)
            display_message(screen, "Game Over!", RED)
            pygame.quit()
            exit()

        # Reset Pac-Man position and update the maze immediately
        grid[pacman_pos[0]][pacman_pos[1]] = 0
        grid[ghost["pos"][0]][ghost["pos"][1]] = 0
        # Now reset logical positions
        ghost["pos"] = ghost["start"]
        pacman_pos = (7, 7)
        # Now update grid to show new positions
        grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
        grid[pacman_pos[0]][pacman_pos[1]] = 2
        current_direction = None
        last_direction = None

def display_message(screen, message, color = WHITE):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    # pygame.time.delay(2000)

def draw_maze(screen, ghost1, ghost2, ghost3, pacman) -> None:
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * GRID_SIZE, row_idx * GRID_SIZE
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            elif cell == 2:
                screen.blit(pacman, (pacman_pos[1] * GRID_SIZE, pacman_pos[0] * GRID_SIZE))
            elif cell == 3:
                screen.blit(ghost1, (ghosts[1]["pos"][1] * GRID_SIZE, ghosts[1]["pos"][0] * GRID_SIZE))
            elif cell == 4:
                screen.blit(ghost2, (ghosts[2]["pos"][1] * GRID_SIZE, ghosts[2]["pos"][0] * GRID_SIZE))
            elif cell == 5:
                screen.blit(ghost3, (ghosts[3]["pos"][1] * GRID_SIZE, ghosts[3]["pos"][0] * GRID_SIZE))

def tuple_add(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]

def inverse_tuple(t1: tuple[int, int]) -> tuple[int, int]:
    return -t1[0], -t1[1]

def bfs_alg(ghost_id):
    global pacman_pos
    ghost = ghosts[ghost_id]
    visit_grid = copy.deepcopy(grid)  # deep copy
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    q = queue.Queue()
    q.put(pacman_pos)
    visited = set()
    visited.add(pacman_pos)
    visit_grid[pacman_pos[0]][pacman_pos[1]] = 6  # mark start
    counter = 7
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
                    elif (r, c) == tuple(ghost["pos"]):
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
    last_sync = time.time()
    last_direction_time = time.time()
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
    pygame.display.set_caption("pacman1")
    pacman = pygame.image.load('images/pacman.png').convert_alpha()
    ghost1 = pygame.image.load('images/ghost1.png').convert_alpha()
    ghost2 = pygame.image.load('images/ghost2.png').convert_alpha()
    ghost3 = pygame.image.load('images/ghost3.png').convert_alpha()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 0))
    print(f"[+] Listening on {server_socket.getsockname()} (IP, port)")
    client_sockets = [server_socket]
    clients = set()

    running = True
    while running:
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
            ghost_id = current_ghost
            move_ghost(ghost_id, current_direction, screen, clients, server_socket)

        # poll for incoming udp packets
        readlist, _, _ = select.select(client_sockets, [], [], 0.1)
        for sock in readlist:
            try:
                data, addr = sock.recvfrom(1024) # if data is connect flag send ack back
                print(f"Received {data} from {addr}")
                if addr not in clients:
                    clients.add(addr)
                    sock.sendto(b"b", addr)
                try:
                    client_id_recv, packet_type_recv, value1, value2, seq = struct.unpack("BBBBB", data)
                    ghost = ghosts[client_id_recv]
                    if seq <= ghost["seq"]:
                        continue
                    ghost["seq"] = seq
                except struct.error as e:
                    print(e)
                    continue
                # print(f"Parsed: client_id={client_id_recv}, packet_type={packet_type_recv}, direction={direction}")
                # print("Active client ports:", [c[1] for c in clients])

                if client_id_recv:
                    ghost_id = client_id_recv
                    ghost = ghosts[ghost_id]
                    if packet_type_recv == 1:
                        direction = value1
                        if direction != 0:
                            if direction == 1:
                                ghost["direction"] = "UP"
                            elif direction == 2:
                                ghost["direction"] = "DOWN"
                            elif direction == 3:
                                ghost["direction"] = "LEFT"
                            elif direction == 4:
                                ghost["direction"] = "RIGHT"
                        move_ghost(ghost_id, ghost["direction"], screen, clients, server_socket)
                        ghost["skip_frame"] = True
                    if packet_type_recv == 2:
                        grid[ghost["pos"][0]][ghost["pos"][1]] = 0
                        row = value1
                        col = value2
                        ghost["pos"] = row, col
                        grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
                    if packet_type_recv == 3:
                        grid[ghost["pos"][0]][ghost["pos"][1]] = 0
                        ghost["pos"] = ghost["start"]
                        grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
                        ghost["direction"] = None
                    if packet_type_recv == 4:
                        grid[ghost["pos"][0]][ghost["pos"][1]] = 0
                        # ghost["pos"] = None
            except socket.timeout:
                pass

        if ghosts[2]["skip_frame"] is False:
            move_ghost(2, ghosts[2]["direction"], screen, clients, server_socket)
        ghosts[2]["skip_frame"] = False
        # move_ghost(3, ghosts[3]["direction"], screen)

        # Interest management & Delta compressions
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

            ghost = ghosts[current_ghost]
            ghost["seq"] += 1
            seq = ghost["seq"]

            # Send direction data
            packet_type_send = 1  # 1 means position
            client_id_send = current_ghost  # from ghost1
            packet = struct.pack("BBBBB", client_id_send, packet_type_send, direction_send, 0, seq)
            for client in clients:
                server_socket.sendto(packet, client)
                print(f"Sent packet to {client}: {packet}")

        # if time.time() - last_sync >= 2:
        #     ghost = ghosts[current_ghost]
        #     ghost["seq"] += 1
        #     seq = ghost["seq"]
        #     ghost_id = current_ghost
        #     row, col = ghost["pos"]
        #     packet_type = 2  # 2 for sync
        #     packet = struct.pack("BBBBB", ghost_id, packet_type, row, col, seq)
        #     print("packet:", packet)
        #     for client in clients:
        #         server_socket.sendto(packet, client)
        #         print(f"Sent sync to {client}: {packet}")
        #     last_sync = time.time()

        draw_maze(screen, ghost1, ghost2, ghost3, pacman)
        pygame.display.flip()
        clock.tick(2) # for adding the sync

if __name__ == "__main__":
    main()
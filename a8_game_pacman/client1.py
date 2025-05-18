import socket
import select
import pygame
import struct
import time
import os
import random
from .map_big import grid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    1: {"pos": (2, 1), "pixel_pos": (1 * GRID_SIZE, 1 * GRID_SIZE), "start": (2, 1), "cell": 3, "direction": None,
        "seq": 0, "skip_frame": False},
    2: {"pos": (2, 17), "pixel_pos": (1 * GRID_SIZE, 17 * GRID_SIZE), "start": (2, 17), "cell": 4, "direction": None,
        "seq": 0, "skip_frame": False},
    3: {"pos": (20, 1), "pixel_pos": (20 * GRID_SIZE, 1 * GRID_SIZE), "start": (20, 1), "cell": 5, "direction": None,
        "seq": 0, "skip_frame": False},
    4: {"pos": (20, 17), "pixel_pos": (20 * GRID_SIZE, 17 * GRID_SIZE), "start": (20, 17), "cell": 6, "direction": None,
        "seq": 0, "skip_frame": False}
}

# Initialize game variables
lives = 20
score = 0
game_over = False
current_direction = None
last_direction = None
direction_send = 0
client_id_recv = 0
packet_type_recv = 0
pacman_pos = (10, 9)
MAX_RECENT = 2
recent_packets = {}
received_seqs = set()


def save_recent_packet(seq, packet):
    recent_packets[seq] = packet
    if len(recent_packets) > MAX_RECENT:
        print("Too many packets to save: ", recent_packets)
        oldest = min(recent_packets.keys())
        del recent_packets[oldest]


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

    if (0 <= new_row < GRID_HEIGHT and 0 <= new_col < GRID_WIDTH and
            grid[new_row][new_col] != 1 and grid[new_row][new_col] not in [4, 5, 6]):
        grid[row][col] = 0  # Clear old position
        grid[new_row][new_col] = ghost["cell"]  # Move ghost
        ghost["pos"] = (new_row, new_col)

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
            save_recent_packet(seq, packet)
            print("packet", packet)
            for client in clients:
                server_socket.sendto(packet, client)
        if lives == 0:
            packet_type = 4
            ghost_id_send = ghost_id
            seq = ghost["seq"] + 1
            ghost["seq"] = seq
            packet = struct.pack("BBBBB", ghost_id_send, packet_type, 0, 0, seq)
            save_recent_packet(seq, packet)
            print("packet", packet)
            for client in clients:
                server_socket.sendto(packet, client)
            display_message(screen, "Game Over!", RED)
            pygame.quit()
            exit()

        grid[pacman_pos[0]][pacman_pos[1]] = 0
        grid[ghost["pos"][0]][ghost["pos"][1]] = 0
        ghost["pos"] = ghost["start"]
        pacman_pos = (10, 9)
        grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
        grid[pacman_pos[0]][pacman_pos[1]] = 2
        current_direction = None
        last_direction = None


def display_message(screen, message, color=WHITE):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)


def draw_maze(screen, ghost1, ghost2, ghost3, ghost4, pacman) -> None:
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
            elif cell == 6:
                screen.blit(ghost4, (ghosts[4]["pos"][1] * GRID_SIZE, ghosts[4]["pos"][0] * GRID_SIZE))


def get_random_direction():
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    valid_directions = []

    for direction in directions:
        new_row, new_col = pacman_pos
        if direction == "UP":
            new_row -= 1
        elif direction == "DOWN":
            new_row += 1
        elif direction == "LEFT":
            new_col -= 1
        elif direction == "RIGHT":
            new_col += 1

        if (0 <= new_row < GRID_HEIGHT and 0 <= new_col < GRID_WIDTH and
                grid[new_row][new_col] != 1):
            valid_directions.append(direction)

    return random.choice(valid_directions) if valid_directions else None


def main(server_socket: socket, clients: list) -> None:
    global current_direction, last_direction, direction_send, client_id_recv, packet_type_recv, pacman_pos
    last_sync = time.time()
    last_redundant_send = time.time()

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
    pygame.display.set_caption("Ghost Client 1")
    pacman_img = pygame.image.load(os.path.join(BASE_DIR, 'images/pacman.png')).convert_alpha()
    ghost1_img = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost1.png')).convert_alpha()
    ghost2_img = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost2.png')).convert_alpha()
    ghost3_img = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost3.png')).convert_alpha()
    ghost4_img = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost4.png')).convert_alpha()

    client_sockets = [server_socket]
    running = True

    while running:
        screen.fill(BLACK)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 30)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (GRID_WIDTH * GRID_SIZE - 100, GRID_SIZE // 4))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_direction = "UP"
                elif event.key == pygame.K_DOWN:
                    current_direction = "DOWN"
                elif event.key == pygame.K_LEFT:
                    current_direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    current_direction = "RIGHT"

        ghost_id = current_ghost
        if current_direction:
            move_ghost(ghost_id, current_direction, screen, clients, server_socket)

        # Handle incoming packets
        readlist, _, _ = select.select(client_sockets, [], [], 0.01)
        for sock in readlist:
            try:
                data, addr = sock.recvfrom(1024)
                try:
                    client_id_recv, packet_type_recv, value1, value2, seq = struct.unpack("BBBBB", data)
                    ghost = ghosts[client_id_recv]
                    if seq in received_seqs:
                        continue
                    received_seqs.add(seq)
                    ghost["seq"] = seq

                    if client_id_recv:
                        ghost_id = client_id_recv
                        ghost = ghosts[ghost_id]
                        if packet_type_recv == 1:  # Direction packet
                            if value1 == 1:
                                ghost["direction"] = "UP"
                            elif value1 == 2:
                                ghost["direction"] = "DOWN"
                            elif value1 == 3:
                                ghost["direction"] = "LEFT"
                            elif value1 == 4:
                                ghost["direction"] = "RIGHT"
                        elif packet_type_recv == 2:  # Position sync
                            grid[ghost["pos"][0]][ghost["pos"][1]] = 0
                            ghost["pos"] = (value1, value2)
                            grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
                        elif packet_type_recv == 3:  # Life lost
                            grid[ghost["pos"][0]][ghost["pos"][1]] = 0
                            ghost["pos"] = ghost["start"]
                            grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
                            ghost["direction"] = None
                        elif packet_type_recv == 4:  # Game over
                            grid[ghost["pos"][0]][ghost["pos"][1]] = 0
                        elif packet_type_recv == 5:  # Pacman position
                            pacman_pos = (value1, value2)
                            grid[value1][value2] = 2
                except struct.error as e:
                    print(e)
                    continue
            except socket.timeout:
                pass

        # Move other ghosts based on received directions
        for ghost_id in [2, 3]:
            if ghosts[ghost_id]["direction"]:
                move_ghost(ghost_id, ghosts[ghost_id]["direction"], screen, clients, server_socket)

        # Send direction updates
        if current_direction != last_direction and current_direction is not None:
            direction_send = {
                "UP": 1,
                "DOWN": 2,
                "LEFT": 3,
                "RIGHT": 4
            }.get(current_direction, 0)

            ghost = ghosts[current_ghost]
            ghost["seq"] += 1
            seq = ghost["seq"]

            packet = struct.pack("BBBBB", current_ghost, 1, direction_send, 0, seq)
            save_recent_packet(seq, packet)
            for client in clients:
                server_socket.sendto(packet, client)
                print(f"Sent packet to {client}: {packet}")

            last_direction = current_direction

        # Periodic sync
        if time.time() - last_sync >= 1:
            ghost = ghosts[current_ghost]
            ghost["seq"] += 1
            seq = ghost["seq"]
            row, col = ghost["pos"]
            packet = struct.pack("BBBBB", current_ghost, 2, row, col, seq)
            save_recent_packet(seq, packet)
            for client in clients:
                server_socket.sendto(packet, client)
                print(f"Sent sync to {client}: {packet}")
            last_sync = time.time()

        # Redundant packet sending
        if time.time() - last_redundant_send >= 4:
            ghost = ghosts[current_ghost]
            seq = ghost["seq"]
            for client in clients:
                for s in range(seq, seq - 2, -1):
                    if s in recent_packets:
                        server_socket.sendto(recent_packets[s], client)
                        print(f"Periodic redundant packet sent: seq {s}")
            last_redundant_send = time.time()

        draw_maze(screen, ghost1_img, ghost2_img, ghost3_img, ghost4_img, pacman_img)
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
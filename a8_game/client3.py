import socket
import select
import pygame
import queue
import copy
import struct
import time
import os
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

current_ghost = 3
ghosts = {
    1: {"pos": (2, 1), "pixel_pos": (1 * GRID_SIZE, 1 * GRID_SIZE), "start": (2, 1), "cell": 3, "direction": None, "seq": 0, "skip_frame": False},
    2: {"pos": (2, 17), "pixel_pos": (1 * GRID_SIZE, 17 * GRID_SIZE), "start": (2, 17), "cell": 4, "direction": None, "seq": 0, "skip_frame": False},
    3: {"pos": (20, 1), "pixel_pos": (20 * GRID_SIZE, 1 * GRID_SIZE), "start": (20, 1), "cell": 5, "direction": None, "seq": 0, "skip_frame": False},
    4: {"pos": (20, 17), "pixel_pos": (20 * GRID_SIZE, 17 * GRID_SIZE), "start": (20, 17), "cell": 6, "direction": None, "seq": 0, "skip_frame": False}
}

# Initialize game variables
lives = 10
score = 0
game_over = False
current_direction = None
last_direction = None
direction_send = 0
client_id_recv = 0
packet_type_recv = 0
pacman_pos = (20, 17)
MAX_RECENT = 2
recent_packets = {}
received_seqs = set()
ping_rtts = {}
ping_send_times = {}

def save_recent_packet(seq, packet):
    recent_packets[seq] = packet
    if len(recent_packets) > MAX_RECENT:
        print("Too many packets to save: ", recent_packets)
        oldest = min(recent_packets.keys())
        del recent_packets[oldest]

def move_ghost(ghost_id, direction, screen, clients, client_socket) -> None:
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

    # if grid[new_row][new_col] != 1 and grid[new_row][new_col] != 3 and grid[new_row][new_col] != 4 and grid[new_row][new_col] != 6:
    if grid[new_row][new_col] != 1:
        grid[row][col] = 0  # Clear old position
        grid[new_row][new_col] = ghost["cell"]  # Move ghost
        ghost["pos"] = (new_row, new_col)

    check_collision(ghost_id, screen, clients, client_socket)

def move_pacman(ghost_id, screen, clients, client_socket) -> None:
    global pacman_pos

    print("Pacman moved")
    print("Pacman position:", pacman_pos)
    # direction = bfs_alg(ghost_id)
    # pacman_pos = tuple_add(pacman_pos, direction)
    check_collision(ghost_id, screen, clients, client_socket)

def tuple_add(t1: tuple[int, int], t2: tuple[int, int]) -> tuple[int, int]:
    return t1[0] + t2[0], t1[1] + t2[1]
def inverse_tuple(t1: tuple[int, int]) -> tuple[int, int]:
    return -t1[0], -t1[1]

def check_collision(ghost_id, screen, clients, client_socket):
    global lives, current_direction, pacman_pos
    pacman_pos = ghosts[4]["pos"]
    ghost = ghosts[ghost_id]
    if ghost["pos"] == pacman_pos and ghost_id != 4:
        local_rtt = ping_rtts.get(ghost_id, 0)
        arbitration_time = time.time() - (local_rtt / 2)
        print(f"Ghost {ghost_id} adjusted event time: {arbitration_time:.6f}s (RTT={local_rtt:.3f}s)")
        lives -= 1
        if lives > 0:
            packet_type = 3
            ghost_id_send = ghost_id
            seq = ghost["seq"] + 1
            ghost["seq"] = seq
            packet = struct.pack("!BBBBH", ghost_id_send, packet_type, 0, 0, seq)
            # save_recent_packet(seq, packet)
            print("packet", packet)
            for client in clients:
                client_socket.sendto(packet, client)
            # display_message(screen, "You lost a life!", RED)
        if lives == 0:
            packet_type = 4
            ghost_id_send = ghost_id
            seq = ghost["seq"] + 1
            ghost["seq"] = seq
            packet = struct.pack("!BBBBH", ghost_id_send, packet_type, 0, 0, seq)
            # save_recent_packet(seq, packet)
            print("packet", packet)
            for client in clients:
                client_socket.sendto(packet, client)
            display_message(screen, "Game Over!", RED)
            pygame.quit()
            exit()

        # Reset Pac-Man position and update the maze immediately
        # grid[pacman_pos[0]][pacman_pos[1]] = 0
        grid[ghost["pos"][0]][ghost["pos"][1]] = 0
        # Now reset logical positions
        ghost["pos"] = ghost["start"]
        # pacman_pos = (20, 17)
        # Now update grid to show new positions
        grid[ghost["pos"][0]][ghost["pos"][1]] = ghost["cell"]
        # grid[pacman_pos[0]][pacman_pos[1]] = 2
        current_direction = None
        last_direction = None

def display_message(screen, message, color = WHITE):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(GRID_WIDTH * GRID_SIZE // 2, GRID_HEIGHT * GRID_SIZE // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)

def draw_maze(screen, ghost1, ghost2, ghost3, ghost4) -> None:
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x, y = col_idx * GRID_SIZE, row_idx * GRID_SIZE
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
            # elif cell == 2:
            #     screen.blit(pacman, (pacman_pos[1] * GRID_SIZE, pacman_pos[0] * GRID_SIZE))
            elif cell == 3:
                screen.blit(ghost1, (ghosts[1]["pos"][1] * GRID_SIZE, ghosts[1]["pos"][0] * GRID_SIZE))
            elif cell == 4:
                screen.blit(ghost2, (ghosts[2]["pos"][1] * GRID_SIZE, ghosts[2]["pos"][0] * GRID_SIZE))
            elif cell == 5:
                screen.blit(ghost3, (ghosts[3]["pos"][1] * GRID_SIZE, ghosts[3]["pos"][0] * GRID_SIZE))
            elif cell == 6:
                screen.blit(ghost4, (ghosts[4]["pos"][1] * GRID_SIZE, ghosts[4]["pos"][0] * GRID_SIZE))

def main(server_socket: socket, clients: list) -> None:
    start_flag = None
    # start_flag = input("Press start flag: ")
    global current_direction, last_direction, direction_send, client_id_recv, packet_type_recv, last_sync
    last_sync = time.time()
    last_redundant_send = time.time()
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
    pygame.display.set_caption("ghost3")
    # pacman = pygame.image.load(os.path.join(BASE_DIR, 'images/pacman.png')).convert_alpha()
    ghost1 = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost1.png')).convert_alpha()
    ghost2 = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost2.png')).convert_alpha()
    ghost3 = pygame.image.load(os.path.join(BASE_DIR, 'images/ghost3.png')).convert_alpha()
    ghost4 = pygame.image.load(os.path.join(BASE_DIR, 'images/pacman.png')).convert_alpha()

    client_sockets = [server_socket]

    running = True
    while running:
        screen.fill(BLACK)
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        # screen.blit(score_text, (10, GRID_SIZE // 4))
        screen.blit(lives_text, (GRID_WIDTH * GRID_SIZE - 100, GRID_SIZE // 4))

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
        ghost_id = current_ghost
        if current_direction:
            move_ghost(ghost_id, current_direction, screen, clients, server_socket)
        # if start_flag == "s":
        # move_pacman(ghost_id, screen, clients, server_socket)

        # Receive direction data
        readlist, _, _ = select.select(client_sockets, [], [], 0.01)
        for sock in readlist:
            try:
                data, addr = sock.recvfrom(1024)
                try:
                    client_id_recv, packet_type_recv, value1, value2, seq = struct.unpack("!BBBBH", data)
                    ghost = ghosts[client_id_recv]
                except struct.error as e:
                    print(e)
                    continue
                # print(f"Parsed: client_id={client_id_recv}, packet_type={packet_type_recv}, direction={direction}")
                # print("Active client ports:", [c[1] for c in clients])

                if client_id_recv:
                    ghost_id = client_id_recv
                    ghost = ghosts[ghost_id]
                    if packet_type_recv == 1:
                        if seq in received_seqs:
                            continue
                        received_seqs.add(seq)

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
                        # move_ghost(ghost_id, ghost["direction"], screen, clients, server_socket)
                        # ghost["skip_frame"] = True
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
                        ghost["alive"] = False
                        clients.remove(addr)
                    if packet_type_recv == 5:
                        pacman_pos = (value1, value2)
                        grid[value1][value2] = 2

            except socket.timeout:
                pass

        # if ghosts[1]["skip_frame"] is False:
        move_ghost(1, ghosts[1]["direction"], screen, clients, server_socket)
        # ghosts[1]["skip_frame"] = False
        # if ghosts[2]["skip_frame"] is False:
        move_ghost(2, ghosts[2]["direction"], screen, clients, server_socket)
        # ghosts[2]["skip_frame"] = False
        move_ghost(4, ghosts[4]["direction"], screen, clients, server_socket)

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
            packet = struct.pack("!BBBBH", client_id_send, packet_type_send, direction_send, 0, seq)
            save_recent_packet(seq, packet)
            for client in clients:
                server_socket.sendto(packet, client)
                print(f"Sent packet to {client}: {packet}")

        if time.time() - last_sync >= 0.5:
            ghost = ghosts[current_ghost]
            ghost["seq"] += 1
            seq = ghost["seq"]
            ghost_id = current_ghost
            row, col = ghost["pos"]
            packet_type = 2  # 2 for sync (ping)
            packet = struct.pack("!BBBBH", ghost_id, packet_type, row, col, seq)
            ping_send_times[seq] = time.time()
            for client in clients:
                server_socket.sendto(packet, client)
                print(f"Sent sync (ping) to {client}: {packet}")
            last_sync = time.time()

        if time.time() - last_redundant_send >= 4:
            ghost = ghosts[current_ghost]
            seq = ghost["seq"]
            for client in clients:
                for s in range(seq, seq - 2, -1):
                    if s in recent_packets:
                        server_socket.sendto(recent_packets[s], client)
                        print(f"Periodic redundant packet sent: seq {s}")
            last_redundant_send = time.time()

        draw_maze(screen, ghost1, ghost2, ghost3, ghost4)
        pygame.display.flip()
        clock.tick(15)

if __name__ == "__main__":
    main()
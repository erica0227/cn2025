import socket
import select
import ipaddress
import random
import threading
import json
import sys

def get_local_ip() -> str:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.connect(("1.1.1.1", 80))
        ip = server_socket.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        server_socket.close()
    return ip

def scan_ip(ip, hosts: dict[str, tuple[str, int]]):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.settimeout(0.5)
        try:
            for i in range(60000, 60100):
                server_socket.sendto(b"ping", (ip, i))
                addr: tuple[str, int]
                data, addr = server_socket.recvfrom(1024)
                if data:
                    print(f"Received from {addr}:{data}")
                    data_encoded = data.decode()
                    if not data.startswith("pong"):
                        continue
                    host = data_encoded.split(" ", maxsplit=1)
                    hosts[host[1]] = addr
        except (socket.timeout, ConnectionRefusedError):
            pass
        except Exception as e:
            print(f"{ip}:{i} - {e}")

def check_ips():
    local_ip = get_local_ip()
    network = ipaddress.ip_network(local_ip + "/22", strict=False)
    hosts: dict[str, tuple[str, int]] = {}
    threads = []
    for ip in network.hosts():
        if str(ip) == local_ip:
            continue
        t = threading.Thread(target=scan_ip, args=(str(ip), hosts))
        t.start()
        threads.append(t)
    t = threading.Thread(target=scan_ip, args=("0.0.0.0", hosts))
    t.start()
    threads.append(t)
    for t in threads:
        t.join()
    return hosts

def start_as_host():
    hostname = input("Enter hostname: ")
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = random.randint(60000, 60099)
    host_socket.bind(('0.0.0.0', port))
    print(f"listening on {host_socket.getsockname()}")
    clients = []
    inputs = [host_socket, sys.stdin]
    while True:
        for readlist in select.select(inputs, [], [], 0.1):
            for read in readlist:
                if read == sys.stdin:
                    # check if input starts with start, if so, start game
                    keyboard_input = sys.stdin.readline().strip()
                    if keyboard_input.startswith("start"):
                        for client in clients:
                            host_socket.sendto(b"start", client)
                            print(client)
                        from .client1 import main
                        return main(host_socket, clients)
                if read == host_socket:
                    data, addr = host_socket.recvfrom(1024)
                    if data == b"ping":
                        host_socket.sendto(f"pong {hostname}".encode())
                        continue
                    if addr not in clients:
                        # new client join
                        print(f"New client joined: {addr}")
                        for client in clients:
                            host_socket.sendto(b"new:" + json.dumps(addr).encode(), client)
                        host_socket.sendto(json.dumps(clients).encode(), addr)
                        clients.append(addr)
                        print(clients)

def join_game() -> None:
    hosts = check_ips()
    host_names = list(hosts.keys())
    if len(host_names) == 0:
        print("No hosts found")
        ip = input("ip: ")
        port = int(input("port: "))
        hostname = input("hostname: ")
        hosts[hostname] = (ip, port)
        host_names = list(hosts.keys())
    index = 1
    print("Please select a host")
    for host_name in host_names:
        print(f"{index}) {host_name}")
    hostname = host_names[int(input()) - 1]
    host_info = hosts[hostname]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(('0.0.0.0', random.randint(60000, 60099)))
    client_socket.sendto(b"connect", host_info)
    data, addr = client_socket.recvfrom(1024)
    # hosts = json.loads(data.decode())
    hosts = [tuple(h) for h in json.loads(data.decode())]
    print(hosts)
    if len(hosts) == 0:
        player = 2
    elif len(hosts) == 1:
        player = 3
    else:
        raise Exception("no fourth wheels allowed")
    hosts.append(addr)
    while True:
        data, addr = client_socket.recvfrom(1024)
        # print(data)
        if data.startswith(b"new:"):
            new_addr = tuple(json.loads(data[4:].decode()))
            hosts.append(new_addr)
            print("New client joined:", new_addr)
        elif data.startswith(b"start"):
            print("Player: ", player)
            if player == 2:
                from .client2 import main
                return main(client_socket, hosts)
            else:
                from .client3 import main
                return main(client_socket, hosts)

def main() -> None:
    choice = input("Enter 1 to host or 2 to join: ")
    if choice == "1":
        start_as_host()
    elif choice == "2":
        join_game()
    else:
        print("Invalid input")

if __name__ == "__main__":
    main()
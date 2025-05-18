import socket
import select
import ipaddress
import random
import threading
import pygame
import struct
import sys
import json

'''
lobby start the server or join the server
main:
ask for input 1 = create server become host
2 = look for server and join
if 1 selected:
    ask for hostname
    select random port
    start hosting on port
    if someone joins send the Ip and port of that person to all other clients
    send the new client all the other clients their information
    lets say 1 2 and 3 are connected and 4 joins
    1 sends the information of 4 to 3 and 2 + 1 sends the information about 2 and 3 to 4
    if host inputs start then the host sends start signal to everyone and moves into the game in the way showed
    below 
if 2 selected:

    display all found hosts in a list like so:
    selection number and hostname for example:
    (1) matthijs
    (2) ishita
    (3) erica
    selection number is just a way to select which host to join
    send host that you want to join a join request and save all the IPs that you get from the host 
    and save your player number
    wait for more clients to join or start signal
    if start signal:
        move to your client file like showed here: 
            player =1 #would be assignent by host
            if player == 1:
                from client1 import main
            elif player == 2:
                from client2 import main
            # after everyone in lobby and host send signal
            # main(server_socket, ips)
'''


def local_ip_addr() -> str:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.connect(("1.1.1.1", 80))
        ip = server_socket.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        server_socket.close()
    return ip


def ip_scanning(ip, hosts: dict[str, tuple[str, int]]):
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
    local_ip = local_ip_addr()
    network = ipaddress.ip_network(local_ip + "/22", strict=False)
    hosts: dict[str, tuple[str, int]] = {}
    threads = []
    for ip in network.hosts():
        if str(ip) == local_ip:
            continue
        t = threading.Thread(target=ip_scanning, args=(str(ip), hosts))
        t.start()
        threads.append(t)
    t = threading.Thread(target=ip_scanning, args=("0.0.0.0", hosts))
    t.start()
    threads.append(t)
    for t in threads:
        t.join()
    return hosts


def main() -> None:
    choice = input("Select 1 to create the game or 2 to join: ")
    if choice == "1":
        hostname = input("Enter Hostname: ")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', random.randint(60000, 60099)))
        hosts = []  # list for all connected clients
        # sys.stdin is input buffer from terminal
        poll_list = [server_socket.fileno(), sys.stdin.fileno()]
        print(f"listening on {server_socket.getsockname()}")
        polling = True
        while polling:
            for readlist in select.select(poll_list, [], [], 0.1):
                for read in readlist:
                    if read == sys.stdin.fileno():  # check if input starts with start, if so, start game
                        if sys.stdin.readline().startswith("start"):
                            for host in hosts:
                                server_socket.sendto(b"s", host)
                                print(host)
                            from .client1 import main
                            print(f"check hosts1: {hosts}")
                            return main(server_socket, hosts)
                    if read == server_socket.fileno():
                        data, addr = server_socket.recvfrom(1024)
                        if data == b"ping":
                            server_socket.sendto(f"pong f{hostname}")  # change .encode(), addr
                            continue #if ping sent and responded with ping then continue
                        print(data)
                        if addr in hosts:
                            continue
                        for client in hosts:
                            server_socket.sendto(b"\x89" + json.dumps(addr).encode(), client)#used to inform clients that the new client has joined
                        server_socket.sendto(json.dumps(hosts).encode(), addr)
                        # Add the new client to the hosts list first
                        hosts.append(addr)

                        print(hosts)
        return None
    elif choice == "2":
        hosts = check_ips()
        host_names = list(hosts.keys())
        if len(host_names) == 0:
            print("No hosts found")
            ip = input("ip: ")
            port = int(input("port: "))
            hostname = input("hostname: ")
            hosts[hostname] = (ip, port)
            host_names = list(hosts.keys())
        counter = 1
        print("please select a host")
        for host_name in host_names:
            print(f"{counter}) {host_name}")
        hostname = host_names[int(input()) - 1]
        host_info = hosts[hostname]
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('0.0.0.0', random.randint(60000, 60099)))
        server_socket.sendto(b"connect", host_info)
        data, addr = server_socket.recvfrom(1024)
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
            data, addr = server_socket.recvfrom(1024)
            print(data)
            if data.startswith(b"\x89"):
                hosts.append(tuple(json.loads(data[1:].decode())))
                print("if x89")
            elif data.startswith(b"s"):
                print("player: ", player)
                if player == 2:
                    from .client2 import main
                    print(f"check hosts2: {hosts}")
                    return main(server_socket, hosts)
                else:
                    from .client3 import main
                    print(f"check hosts3: {hosts}")
                    return main(server_socket, hosts)
    else:
        print("[!] Invalid choice")
        return None


if __name__ == "__main__":
    main()
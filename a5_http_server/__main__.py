import json
import os
import select
import socket
from argparse import ArgumentParser, Namespace

file_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(file_path, "mime.json"), "r") as f:
    mime = json.load(f)

def get_file_type(path):
    extension = path.split(".")[-1]
    if extension in mime:
        return mime[extension]
    else:
        return "text/plain"

def parse_arguments() -> Namespace:
    """
    Parse command line arguments for the http server.
    The three valid options are:
        --address: The host to listen at. Default is "0.0.0.0"
        --port: The port to listen at. Default is 8000
        --directory: The directory to serve. Default is "data"
    :return: The parsed arguments in a Namespace object.
    """


    parser: ArgumentParser = ArgumentParser(
        prog="python -m a5_http_server",
        description="A5 HTTP Server assignment for the VU Computer Networks course.",
        epilog="Authors: Your group name"
    )
    parser.add_argument("-a", "--address",
                        type=str, help="Set server address", default="0.0.0.0")
    parser.add_argument("-p", "--port",
                        type=int, help="Set server port", default=8000)
    parser.add_argument("-d", "--directory",
                        type=str, help="Set the directory to serve", default="a5_http_server/public")

    return parser.parse_args()

def main() -> None:
    parser: Namespace = parse_arguments()
    port: int = parser.port
    host: str = parser.address
    base_directory: str = parser.directory

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    address_port = (host, port)
    listen_socket.bind(address_port)
    listen_socket.listen()
    print(f"Server listening on {host}: {port}")
    sock_list: list[socket.socket] = [listen_socket]

    while True:
        read_list, _, _ = select.select(sock_list, [], [])
        # timeout of 0 seconds, makes the method call non-blocking
        if read_list:
            for sock in read_list:
                if sock is listen_socket:
                    client_socket, _ = sock.accept()
                    sock_list.append(client_socket)
                try:
                    receive_msg(client_socket, base_directory)
                except socket.timeout:
                    listen_socket.close()
                    sock_list.remove(sock)

class Headers:
    def __init__(self):
        self.headers = {}

    def set_header(self, key, val):
        self.headers[key] = val

    def set_status(self, code_status: str):
        self.status_line = f"HTTP/1.1 {code_status}"

    def set_content_type(self, content_type: str):
        self.headers["Content-Type"] = content_type

    def set_content_length(self, length: int):
        self.headers["Content-Length"] = str(length)

    def set_connection(self, keep_alive: bool):
        if keep_alive:
            self.headers["Connection"] = "keep-Alive"
            self.headers["Keep-Alive"] = "timeout=10, max=1000"
        else:
            self.headers["Connection"] = "close"

    def build(self) -> bytes:
        header_str = self.status_line + "\r\n"
        for key, value in self.headers.items():
            header_str += f"{key}: {value}\r\n"
        header_str += "\r\n"
        return header_str.encode("utf-8")

"""
header = (
  "HTTP/1.1 200 OK\r\n"
   "Connection: keep-Alive\r\n"
    "Keep-Alive: timeout=5, max=1000\r\n"
    "Content-Type: text/html\r\n"
    f"Content-Length: {len(body)}\r\n"
    "\r\n"
)
"""

def receive_msg(sock: socket.socket, base_directory: str) -> None:
        client_msg = ""
        while "\r\n\r\n" not in client_msg:
            data = sock.recv(1).decode()
            client_msg += data

        if not client_msg:
            return

        request = client_msg.split(" ")
        request_path = base_directory + request[1]

        header = Headers()
        header.set_status("200 OK")
        header.set_connection(True)

        if  len(request) >= 3 and client_msg.startswith("GET") and request[1].startswith("/"):
            # print(f"Received path: {request_path}"
            if request[2].startswith("HTTP/1.1"):

                if request[1] == "/" or os.path.isdir(request_path):
                    if request_path.endswith("/"):
                        request_path = request_path[:-1]
                    request_path = os.path.join(request_path, "index.html")
                print(request_path)

                if os.path.isfile(request_path):
                    with open(request_path, "rb") as f:
                        body = f.read()

                elif not os.path.exists(request_path):
                    request_path = base_directory + "/404.html"
                    with open(request_path, "rb") as f:
                        body = f.read()
                    header.set_status("404 Not Found")
                    header.set_connection(False)

            else:
                # invalid format
                request_path = base_directory + "/400.html"
                with open(request_path, "rb") as f:
                    body = f.read()
                header.set_status("400 Bad Request")
                header.set_connection(True)

        else:
            # invalid format
            request_path = base_directory + "/400.html"
            with open(request_path, "rb") as f:
                body = f.read()
            header.set_status("400 Bad Request")
            header.set_connection(True)

        header.set_content_type(get_file_type(request_path))
        header.set_content_length(len(body))
        response = header.build() + body
        send_message(response, sock)

def send_message(message: bytes, sock: socket.socket) -> None:
    bytes_len = len(message)
    num_bytes_to_send = bytes_len
    while num_bytes_to_send > 0:
        num_bytes_to_send -= sock.send(message[bytes_len - num_bytes_to_send:])

if __name__ == "__main__":
    main()

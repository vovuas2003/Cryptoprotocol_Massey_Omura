import socket

def main():
    run_example()

def run_example():
    host = "127.0.0.1"
    port = 54321
    who = int(input("0 = Bob (server), 1 = Alice (client): "))
    if who:
        print("I am Alice.")
        run_Alice(host, port)
    else:
        print("I am Bob.")
        run_Bob(host, port)

def run_Alice(host, port):
    Alice_socket = SocketCommunicator()
    Alice_socket.connect_client(host, port)
    Alice_socket.send_message("Alice: Hello, Bob!".encode('utf-8'))
    print(Alice_socket.receive_message().decode('utf-8'))
    Alice_socket.send_message("Alice: Nice, bye-bye))".encode('utf-8'))
    Alice_socket.close()

def run_Bob(host, port):
    Bob_socket = SocketCommunicator()
    Bob_socket.start_server(host, port)
    print(Bob_socket.receive_message().decode('utf-8'))
    Bob_socket.send_message("Bob: Hello, how are you?".encode('utf-8'))
    print(Bob_socket.receive_message().decode('utf-8'))
    Bob_socket.close()

class SocketCommunicator:
    def __init__(self, max_recieved_bytes = 1024):
        self.sock = None
        self.conn = None
        self.is_server = False
        self.max_recieved_bytes = max_recieved_bytes
    def start_server(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        self.is_server = True
    def connect_client(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.is_server = False
    def send_message(self, data):
        if self.is_server and self.conn:
            self.conn.send(data)
        elif not self.is_server and self.sock:
            self.sock.send(data)
        else:
            raise Exception("Error: uninitialised socket!")
    def receive_message(self):
        if self.is_server and self.conn:
            data = self.conn.recv(self.max_recieved_bytes)
        elif not self.is_server and self.sock:
            data = self.sock.recv(self.max_recieved_bytes)
        else:
            raise Exception("Error: uninitialised socket!")
        return data
    def close(self):
        if self.conn:
            self.conn.close()
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    main()

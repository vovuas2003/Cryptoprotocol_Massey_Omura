import numpy as np
import galois
import socket
import threading
import json
import random
import time

DATABASE = None

def main():
    run_CLI()

def run_CLI():
    try:
        p, n, bytes_value, logging = get_json_params()
    except:
        init_json_example_params()
        p, n, bytes_value, logging = get_json_params()
    try:
        database = get_json_database()
    except:
        init_json_example_database()
        database = get_json_database()
    global DATABASE
    DATABASE = database
    Whoami = Participant(p, n, bytes_value, logging)
    name = input("Enter your name: ")
    try:
        serv_ip, serv_port, cli_ip, cli_port = get_net_set_from_database(database, name)
    except:
        return
    Whoami.init_sockets(serv_ip, serv_port, cli_ip, cli_port)
    Whoami.init_name_and_log(name)
    Whoami.run_server()
    try:
        while True:
            msg = random.randint(0, Whoami.N_1)
            print("New random message:", ' '.join(f"{b:02x}" for b in msg.to_bytes(Whoami.bytes_value, byteorder='big')))
            with open(Whoami.name + "_original.bin", "wb") as f:
                f.write(msg.to_bytes(Whoami.bytes_value, byteorder = 'big'))
            print("This message was saved into " + Whoami.name + "_original.bin")
            name = input("Name to send message: ")
            ip, port, _i, _p, = get_net_set_from_database(database, name)
            Whoami.run_client(ip, port, msg)
    except:
        print("Error, emergency exit!")
    finally:
        Whoami.close_all()

def init_json_example_params():
    params = {
        "p": 2,
        "n": 256,
        "bytes": 32,
        "logging": True
    }
    with open("params.json", "w") as f:
        json.dump(params, f, indent = 4)

def get_json_params():
    with open("params.json", "r") as f:
        params = json.load(f)
    p = params["p"]
    n = params["n"]
    bytes_value = params["bytes"]
    logging = params["logging"]
    return p, n, bytes_value, logging

def init_json_example_database():
    database = {
        "Alice": {
            "serv_ip": "127.0.0.1",
            "serv_port": 55001,
            "cli_ip": "127.0.0.1",
            "cli_port": 55002
        },
        "Bob": {
            "serv_ip": "127.0.0.1",
            "serv_port": 55011,
            "cli_ip": "127.0.0.1",
            "cli_port": 55012
        },
        "Charlie": {
            "serv_ip": "127.0.0.1",
            "serv_port": 55021,
            "cli_ip": "127.0.0.1",
            "cli_port": 55022
        }
    }
    with open("database.json", "w") as f:
        json.dump(database, f, indent = 4)

def get_json_database():
    with open("database.json", "r") as f:
        database = json.load(f)
    return database

def get_net_set_from_database(database, name):
    if name in database:
        params = database[name]
        serv_ip = params["serv_ip"]
        serv_port = params["serv_port"]
        cli_ip = params["cli_ip"]
        cli_port = params["cli_port"]
        return serv_ip, serv_port, cli_ip, cli_port
    else:
        print(f"User {name} not found!")
        raise Exception("Not found!")

def get_name_by_net_set(database, ip, port):
    if database == None:
        raise Exception("Uninitialized database!")
    for name, info in database.items():
        if info.get("serv_ip") == ip and info.get("serv_port") == int(port) or info.get("cli_ip") == ip and info.get("cli_port") == int(port):
            return name
    raise Exception("Unknown client!")

class Participant():
    def __init__(self, p, n, bytes_value, logging):
        self.n = n
        self.p = p
        self.bytes_value = bytes_value
        try:
            self.field = galois.GF(p, n)
        except LookupError:
            if p == 2 and n == 256: # field.properties
                irr_poly = "x^256 + x^10 + x^5 + x^2 + 1"
                prim_ele = "x"
                self.field = galois.GF(p, n, irreducible_poly = irr_poly, primitive_element = prim_ele)
            else:
                irr_poly = galois.irreducible_poly(p, n)
                self.field = galois.GF(p, n, irreducible_poly = irr_poly, primitive_element = galois.primitive_element(irr_poly))
        except:
            print("Unexpected error in GF init!")
            raise
        self.poly_to_check_gcd = galois.Poly([1 for _ in range(self.n)], field = self.field)
        self.N_1 = self.p**self.n - 1
        self._generate_key()

        self.server_socket = None
        self.client_socket = None
        self.server_running = False

        self.logging = logging
        if self.logging:
            self.log_lock = threading.Lock()
    def _generate_key(self):
        while True:
            self.key = self.field.Random(1)[0]
            if self.key == self.field(0):
                continue
            if self.key == self.field(1):
                continue
            if self._check_gcd() == self.field(1):
                continue
            self.key = int(self.key)
            try:
                self.key_inv = pow(self.key, -1, self.N_1)
                break
            except:
                continue
    def _check_gcd(self):
        return galois.gcd(galois.Poly(self.key.vector()[0], field = self.field), self.poly_to_check_gcd)
    def encrypt(self, message):
        return self.field(message) ** self.key
    def decrypt(self, message):
        return self.field(message) ** self.key_inv
    def init_name_and_log(self, name):
        self.name = name
        if self.logging:
            with self.log_lock:
                with open(self.name + "_log.txt", "w") as f:
                    f.write("time;source;destination;message\n")
    def _append_to_log(self, source, dest, msg):
        if self.logging:
            with self.log_lock:
                with open(self.name + "_log.txt", "a") as f:
                    f.write(f"{time.ctime()};{source};{dest};{msg}\n")
    def init_sockets(self, serv_ip, serv_port, cli_ip, cli_port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((serv_ip, serv_port))
        self.server_socket.listen(5)
        self.cli_ip = cli_ip
        self.cli_port = cli_port
    def run_server(self):
        if not self.server_running:
            self.server_running = True
            self.server_thread = threading.Thread(target = self._server_loop, daemon = True)
            self.server_thread.start()
    def _server_loop(self):
        with self.server_socket:
            while self.server_running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    threading.Thread(target = self._handle_client, args = (client_socket, addr), daemon = True).start()
                except OSError:
                    break
    def _handle_client(self, conn, addr):
        try:
            ip, port = addr[0], addr[1]
            cli_name = get_name_by_net_set(DATABASE, ip, port)
            msg = conn.recv(1024).decode('utf-8')
            self._append_to_log(cli_name, self.name, msg)
            msg = str(int(self.encrypt(int(msg))))
            self._append_to_log(self.name, cli_name, msg)
            conn.sendall(msg.encode('utf-8'))
            msg = conn.recv(1024).decode('utf-8')
            self._append_to_log(cli_name, self.name, msg)
            msg = int(self.decrypt(int(msg)))
            with open(cli_name + "_to_" + self.name + ".bin", "wb") as f:
                f.write(msg.to_bytes(self.bytes_value, byteorder = 'big'))
        except Exception as e:
            print(f"_handle_client: {e}")
        finally:
            conn.close()
    def run_client(self, ip_to_connect, port_to_connect, msg):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.client_socket.bind((self.cli_ip, self.cli_port))
            serv_name = get_name_by_net_set(DATABASE, ip_to_connect, port_to_connect)
            self.client_socket.connect((ip_to_connect, port_to_connect))
            msg = str(int(self.encrypt(msg)))
            self._append_to_log(self.name, serv_name, msg)
            self.client_socket.sendall(msg.encode('utf-8'))
            msg = int(self.client_socket.recv(1024).decode('utf-8'))
            self._append_to_log(serv_name, self.name, msg)
            msg = str(int(self.decrypt(msg)))
            self._append_to_log(self.name, serv_name, msg)
            self.client_socket.sendall(msg.encode('utf-8'))
        except Exception as e:
            print(f"run_client: {e}")
        finally:
            try:
                self.client_socket.close()
            except OSError as e:
                print(f"run_client in close: {e}")
    def close_all(self):
        self.server_running = False
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
            except OSError:
                pass
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except OSError:
                pass
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout = 1)

if __name__ == "__main__":
    main()

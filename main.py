from Massey_Omura import Participant
from my_network_sockets import SocketCommunicator

HOST = "127.0.0.1"
PORT = 54321
P = 2
N = 256

def main():
    run_protocol()

def run_protocol():
    who = int(input("0 = Bob (server, start first), 1 = Alice (client): "))
    if who:
        print("Alice starts protocol.")
        run_Alice()
    else:
        with open("common_params.txt", "w") as f:
            f.write(HOST + ":" + str(PORT) + "\n" + str(P) + "^" + str(N))
        print("Bob starts protocol.")
        run_Bob()
    print("Protocol is finished.")

def run_Alice():
    Alice = Participant(P, N)
    Alice.generate_key()
    with open("Alice_keys.txt", "w") as f:
        f.write(str(Alice.key) + "\n" + str(Alice.key_inv))
    import random
    message = random.randint(0, P**N - 1)
    log = open("Alice_log.txt", "w")
    log.write("original message: " + str(message) + "\n")
    message = Alice.encrypt(message)
    log.write("my encrypted message (to Bob): " + str(message) + "\n")
    Alice_socket = SocketCommunicator()
    Alice_socket.connect_client(HOST, PORT)
    Alice_socket.send_message(str(message).encode('utf-8'))
    message = int(Alice_socket.receive_message().decode('utf-8'))
    log.write("double encrypted message (from Bob): " + str(message) + "\n")
    message = Alice.decrypt(message)
    log.write("encrypted message (to Bob): " + str(message) + "\n")
    log.close()
    Alice_socket.send_message(str(message).encode('utf-8'))
    Alice_socket.close()

def run_Bob():
    Bob = Participant(P, N)
    Bob.generate_key()
    with open("Bob_keys.txt", "w") as f:
        f.write(str(Bob.key) + "\n" + str(Bob.key_inv))
    Bob_socket = SocketCommunicator()
    Bob_socket.start_server(HOST, PORT)
    message = int(Bob_socket.receive_message().decode('utf-8'))
    log = open("Bob_log.txt", "w")
    log.write("encrypted message (from Alice): " + str(message) + "\n")
    message = Bob.encrypt(message)
    log.write("double encrypted message (to Alice): " + str(message) + "\n")
    Bob_socket.send_message(str(message).encode('utf-8'))
    message = int(Bob_socket.receive_message().decode('utf-8'))
    Bob_socket.close()
    log.write("my encrypted message (from Alice): " + str(message) + "\n")
    message = Bob.decrypt(message)
    log.write("recovered message: " + str(message) + "\n")
    log.close()

if __name__ == "__main__":
    main()

import tkinter as tk
import random

from Massey_Omura import Participant
from my_network_sockets import SocketCommunicator

class GUI_Participant():
    def __init__(self):
        self.socket = SocketCommunicator()
    def real_init(self, ip, port, p, n):
        self.ip = ip
        self.port = port
        self.person = Participant(p, n)
    def become_Alice(self):
        self.socket.connect_client(self.ip, self.port)
    def become_Bob(self):
        self.socket.start_server(self.ip, self.port)
    def send_string(self, s):
        self.socket.send_message(s.encode('utf-8'))
    def recv_string(self):
        return self.socket.receive_message().decode('utf-8')
    def gen_keys(self):
        self.person.generate_key()
        return self.person.key, self.person.key_inv
    def enc(self, m):
        return self.person.encrypt(m)
    def dec(self, m):
        return self.person.decrypt(m)
    def close(self):
        self.socket.close()

def mymessagebox(fontsize, butsize, mytitle, mytext):
    toplevel = tk.Toplevel(window)
    toplevel.title(mytitle)
    toplevel.geometry(f"600x400+{window.winfo_x()+40}+{window.winfo_y()+15}")
    toplevel.resizable(False, False)
    l = tk.Label(toplevel, text = mytext, font = ("TkDefaultFont", fontsize))
    l.pack()
    b = tk.Button(toplevel, text = "Close", command = toplevel.destroy, width = 10, font = ("TkDefaultFont", butsize))
    b.pack()

def show_error():
    mymessagebox(30, 30, "Error!", "ERROR!\n\nPress help button\nto show common\nmistakes in usage.\n")

def button0_click():
    mymessagebox(15, 15, "Source code: github.com/vovuas2003/Cryptoprotocol_Massey_Omura", "\nAlice - client, run second. Bob - server, run first.\n\nDon't forget to set network settings\nand common parameters in the first line\n(need to init participant).\n\nThe second line is a message (integer value)\nto transfer from Alice to Bob.\n\nThe third and fourth lines are cryptoprotocol keys.\n\nCryptoprotocol log will be in the big window.\n\n")

def button1_click():
    try:
        settings = entry0.get().split()
        ip, port = settings[0].split(":")
        port = int(port)
        p, n = settings[1].split("^")
        p = int(p)
        n = int(n)
        glob.real_init(ip, port, p, n)
    except:
        show_error()

def button2_click():
    try:
        rand = random.randint(0, glob.person.N_1 + 1)
        entry1.delete(0, tk.END)
        entry1.insert(0, rand)
    except:
        show_error()

def button3_click():
    try:
        k, k_i = glob.gen_keys()
        entry2.delete(0, tk.END)
        entry2.insert(0, k)
        entry3.delete(0, tk.END)
        entry3.insert(0, k_i)
    except:
        show_error()

def button4_click():
    try:
        entry4.delete("1.0", tk.END)
        entry4.insert(tk.END, "Alice starts protocol\n")
        glob.become_Alice()
        message = entry1.get()
        entry4.insert(tk.END, "original message: " + message + "\n")
        message = str(glob.enc(int(message)))
        entry4.insert(tk.END, "my encrypted message (to Bob): " + message + "\n")
        glob.send_string(message)
        message = glob.recv_string()
        entry4.insert(tk.END, "double encrypted message (from Bob): " + message + "\n")
        message = str(glob.dec(int(message)))
        entry4.insert(tk.END, "encrypted message (to Bob): " + message + "\n")
        glob.send_string(message)
        glob.close()
        entry4.insert(tk.END, "Protocol is finished")
    except Exception as e:
        print(f"{e}")
        show_error()

def button5_click():
    try:
        entry4.delete("1.0", tk.END)
        entry4.insert(tk.END, "Bob starts protocol\n")
        glob.become_Bob()
        message = glob.recv_string()
        entry4.insert(tk.END, "encrypted message (from Alice): " + message + "\n")
        message = str(glob.enc(int(message)))
        entry4.insert(tk.END, "double encrypted message (to Alice): " + message + "\n")
        glob.send_string(message)
        message = glob.recv_string()
        glob.close()
        entry4.insert(tk.END, "my encrypted message (from Alice): " + message + "\n")
        message = str(glob.dec(int(message)))
        entry4.insert(tk.END, "recovered message: " + message + "\n")
        entry1.delete(0, tk.END)
        entry1.insert(0, message)
        entry4.insert(tk.END, "Protocol is finished")
    except Exception as e:
        print(f"{e}")
        show_error()

def button6_click():
    try:
        params = entry0.get()
        with open("params.txt", "w") as f:
            f.write(params)
    except:
        show_error()

def button7_click():
    try:
        k = entry2.get()
        k_i = entry3.get()
        with open("keys.txt", "w") as f:
            f.write(k + "\n" + k_i)
    except:
        show_error()

def button8_click():
    try:
        text = entry4.get("1.0", "end-1c")
        with open("log.txt", "w") as f:
            f.write(text)
    except:
        show_error()

def button9_click():
    try:
        msg = entry1.get()
        with open("msg.txt", "w") as f:
            f.write(msg)
    except:
        show_error()

def button10_click():
    try:
        with open("params.txt", "r") as f:
            par = f.read()
        entry0.delete(0, tk.END)
        entry0.insert(0, par)
    except:
        show_error()

def button11_click():
    try:
        with open("keys.txt", "r") as f:
            keys = f.read().splitlines()
        k = int(keys[0])
        k_i = int(keys[1])
        glob.person.key = k
        glob.person.key_inv = k_i
        entry2.delete(0, tk.END)
        entry2.insert(0, k)
        entry3.delete(0, tk.END)
        entry3.insert(0, k_i)
    except:
        show_error()

def button12_click():
    try:
        with open("msg.txt", "r") as f:
            msg = f.read()
        entry1.delete(0, tk.END)
        entry1.insert(0, msg)
    except:
        show_error()

glob = GUI_Participant()

window = tk.Tk()
window.title("Massey-Omura")

frame_buttons = tk.Frame(window)
frame_buttons.pack(side = tk.TOP, fill = tk.X)

buttons = []
but_names = ["help", "init", "gen msg", "gen keys", "Alice", "Bob", "exp params", "exp keys", "exp log", "exp msg", "imp params", "imp keys", "imp msg"]
but_com = [button0_click, button1_click, button2_click, button3_click, button4_click, button5_click, button6_click, button7_click, button8_click, button9_click, button10_click, button11_click, button12_click]
for i in range(13):
    buttons.append(tk.Button(frame_buttons, text = but_names[i], command = but_com[i]))

for button in buttons:
    button.pack(side = tk.LEFT)

entry0 = tk.Entry(window, width = 50)
entry1 = tk.Entry(window, width = 50)
entry2 = tk.Entry(window, width = 50)
entry3 = tk.Entry(window, width = 50)
entry4 = tk.Text(window, height = 20, width = 50)

entry0.insert(0, "ip.add.re.ss:port p^n")
entry1.insert(0, "message, it is a random int value from 0 to (p^n)-1")
entry2.insert(0, "private key for encryption")
entry3.insert(0, "private key for decryption")
entry4.insert("1.0", "Here will be log\n(switch keyboard layout to english to use crtl+c)\n\nYou can't resize window, but can scroll down.")

entry0.pack()
entry1.pack()
entry2.pack()
entry3.pack()
entry4.pack(fill = tk.BOTH, expand = True)

window.resizable(False, False)
window.mainloop()

import socket
import time
import sys
import select
HOST = '0.0.0.0'
PORT = 5000
BUF_SIZE = 1024


class WhatsUpClient():

    def __init__(self, host=HOST, port=PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        temp = 0
        while 1:
            socket_list = [sys.stdin,self.sock]
            ready_to_read,ready_to_write,in_error = select.select(socket_list,[],[])

            for sock_for in ready_to_read:
                if sock_for == self.sock:
                    data = sock_for.recv(4096)
                    if not data:
                        print("Disconnected from chat server")
                        sys.exit()
                    else:
                        sys.stdout.write(data)
                        sys.stdout.flush()
                else:
                    msg = sys.stdin.readline()
                    if temp > 1:
                        sys.stdout.write("<Input> :")
                    temp = temp +1
                    self.sock.send(msg)
                    sys.stdout.flush()

    def run(self):
        pass


def main():
    client = WhatsUpClient()

if __name__ == '__main__':
    main()
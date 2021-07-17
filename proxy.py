import socket
from sys import exit, argv
from threading import Thread


class ProxyServer:
    def __init__(self, remote_server, port_number):
        self.remote_server = remote_server
        self.port_number = port_number
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.server.bind(("***.***.***.***", int(self.port_number)))
        print("[+]bound")
        self.server.listen(10)
        print("[+]listening")

        try:
            while True:
                client, adress = self.server.accept()
                print(f"[+]got connection from: {adress[0]}")

                thread_handler = Thread(target=self.proxy_handler, args=(client,))
                thread_handler.start()
        except KeyboardInterrupt:
            self.server.close()
            self.client_to_server.close()
            exit(-1)
        except Exception as E:
            print(E)

    def proxy_handler(self, client):
        self.client_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_to_server.connect((self.remote_server, int(self.port_number)))

        pcounter = 0

        try:
            while True:
                byted_string = self.recv_data(self.client_to_server)
                if byted_string:
                    pcounter += self.hexdumber(byted_string, pcounter)
                    client.send(byted_string)
                    print("[>]sent to local")

                byted_string = self.recv_data(client)
                if byted_string:
                    self.client_to_server.send(byted_string)
                    pcounter += self.hexdumber(byted_string, pcounter)
                    print("[<]sent to remote")
        except KeyboardInterrupt:
            self.server.close()
            self.client_to_server.close()
            exit(-1)
        except Exception as E:
            print(E)

    def recv_data(self, client):
        client.settimeout(5)
        byted_string = b""
        try:
            while True:
                data = b""
                data += client.recv(4096)
                if data == b"":
                    break
                byted_string += data
        except KeyboardInterrupt:
            self.server.close()
            self.client_to_server.close()
            exit(-1)
        except Exception:
            pass
        return byted_string

    def hexdumber(self, byted_data, pcounter):
        hex_filter = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(128)])
        counter = pcounter
        if isinstance(byted_data, bytes):
            data = byted_data.decode()
        else:
            data = byted_data
        del byted_data

        un_filtered_data = data

        data = data.translate(hex_filter)

        print(f"{counter:08b}", end="   ")
        for char in un_filtered_data:
            print(f"{ord(char):02x}", end=" ")
        print("|  ", end=f"{data}\n")
        counter += 1

        return 1


if __name__ == "__main__":
    print("type: --help for instructions to how to use this program")

    if not len(argv[1:]) != 2 or argv[1] == "--help":
        print("sudo python3 proxy.py [server to connect] [port number to listen]")
    else:
        proxy_server = ProxyServer(remote_server=argv[1], port_number=argv[2])
        proxy_server.run()

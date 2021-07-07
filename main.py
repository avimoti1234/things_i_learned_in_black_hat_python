import socket
import subprocess
from platform import uname
from threading import Thread
import argparse
from textwrap import dedent
from sys import exit

description = dedent(
    '''
    some examples
    python netcat.py -t\\--target <ip> -p\\--port <port number> #conncts to the netcat server
    python netcat.py -t\\--target <ip> -p\\--port <port number> -s\\--server -cs\\--command_shell #starts a command line at the client side
    python netcat.py -t\\--target <ip> -p\\--port <port number> -s\\--server -si\\--system_information #sends the target ip's system informtion to the client
    python netcat.py -t\\--target <ip> -p--port <port number> -s\\--server -c\\--command #sends a command to the netcat client
    ''')

command_options = argparse.ArgumentParser(description="netcat tool 0.1v", formatter_class=argparse.RawTextHelpFormatter,
                                          epilog=description)

command_options.add_argument('-t', "--target", help="enter the target ip")
command_options.add_argument('-cs', "--command_shell", action="store_true",
                             help="starts a command shell at the client side")
command_options.add_argument('-p', "--port", type=int, help="enter a port number")
command_options.add_argument('-c', "--command", action="store_true", help="enter a command that is to executed in the terminal")
command_options.add_argument('-s', "--server", action="store_true",
                             help="if you specify this the netcat program will cat as a remote server")
command_options.add_argument('-si', "--system_information", action="store_true",
                             help="prints the target's system iformation")

arguments = command_options.parse_args()

if (not arguments.target and not arguments.port) or (not arguments.target and arguments.port) or (
        arguments.target and not arguments.port):
    print("[+]ip adress or port number was not specified pls try again")
    exit(-1)


class natcat:
    def __init__(self, arguments):
        self.arguments = arguments
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[+]socket has initialized successfully")

    def run(self):
        if not self.arguments.server:
            self.client_mode()
        else:
            self.server_mode()

    def client_mode(self):
        self.socket.connect((self.arguments.target, self.arguments.port))
        print("[+]client has successfully connected")
        print(self.socket.recv(5000).decode(), end="")
        try:
            while True:
                response = self.socket.recv(5000).decode()
                print(response, end="")
                if not response.isalpha():
                    command = input()
                    if command == "exit":
                        self.socket.close()
                        exit(1)
                    self.socket.send(command.encode())
        except KeyboardInterrupt:
            self.socket.close()
            exit(-1)
        except BrokenPipeError:
            self.socket.close()
            exit(-1)

    def server_mode(self):
        self.socket.bind((str(self.arguments.target), int(self.arguments.port)))
        print("[+]socket has bound successfully")
        self.socket.listen(5)
        print("[+]listening\n\n")
        try:
            while True:
                client, adress = self.socket.accept()
                thread_handler = Thread(target=self.handle_client, args=(client,))
                thread_handler.start()
        except KeyboardInterrupt:
            self.socket.close()
            exit(-1)

    def handle_client(self, client_handler):
        if self.arguments.command_shell:
            client_handler.send(b"to exit the terminal enter: exit\n")
            try:
                while True:
                    client_handler.send(b"\rNT#>")
                    response = client_handler.recv(5000).decode()
                    result = subprocess.run(response, shell=True, capture_output=True)
                    client_handler.send(b"\n" + result.stdout)
            except KeyboardInterrupt:
                client_handler.close()
                exit(-1)
            except subprocess.CalledProcessError as d:
                print(d)
                client_handler.close()
                self.socket.close()
                exit(-1)
            except BrokenPipeError:
                self.socket.close()
                exit(-1)

        elif self.arguments.command:
            client_handler.send(b"\rNT#>")
            response = ""
            while not response:
                response = client_handler.recv(5000).decode()
            result = subprocess.run(response, shell=True, capture_output=True)
            client_handler.send(b"\n" + result.stdout)
            client_handler.close()
            self.socket.close()
            exit(1)

        elif self.arguments.system_information:
            sys_info = dedent(f'''
            ip: {socket.gethostbyname(socket.gethostname())}
            operating system name: {uname().system}
            operating system version: {uname().version}
            operating system processor: {uname().machine}
            operating system release: {uname().release} 
            ''')

            client_handler.send(sys_info.encode())
            client_handler.close()
            exit(1)


if __name__ == "__main__":
    natcatobj = natcat(arguments)
    natcatobj.run()

import socket
import time
import select

class BaseSocketServer(object):
    def __init__(self):
        self.__ip = None
        self.__port = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__headerLength = None
        self.__commandDict = {}
        self.__idleTime = None
        self.__sock_list=[self.__socket]
        self.__clients={}

    def run(self):
        self.__socket.listen()
        print(f"server is working at IP:{self.__ip}, port:{self.__port}")

        while True:
            read_sock, output_sock, except_sock=select.select(self.__sock_list, [], self.__sock_list, 5.0)

            for notified_socket in read_sock:
                notified_socket.settimeout(1)
                if notified_socket == self.__socket:
                    client_socket, address=self.__socket.accept()
                    print(f'connection from {address} has been established.')
                    self.__sock_list.append(client_socket)
                    self.__clients[client_socket] = address
                    continue
                message = self.__messageRecv(notified_socket)
                if not message:
                    print(f'Closed connection from: {self.__clients[notified_socket]}')
                    self.__sock_list.remove(notified_socket)
                    del self.__clients[notified_socket]
                    continue

                functionName, functionParameter= message.split("*")
                f = self.__commandDict.get(functionName)

                f(functionParameter)

            for notified_socket in except_sock:
                self.__sock_list.remove(notified_socket)
                

                # print(notified_socket)
                # print('sleeping....')
                # time.sleep(5)
    def registCommand(self, func):
        self.__commandDict.update({func.__name__:func})
        def wrap(para):
            return func(para)

        return wrap

    def __messageRecv(self, client_socket):
        try:
            header = client_socket.recv(self.__headerLength)
            
            if not len(header):
                print('header error or client stop')
                return ''
            msg_length = int(header.strip())
            msg = client_socket.recv(msg_length)
            return msg.decode()
        except Exception:
            return ''


    @property
    def serverIdleTime(self):
        return self.__idleTime
    
    @serverIdleTime.setter
    def serverIdleTime(self, idleTime:float):
        "idleTime:seconds"
        self.__idleTime = idleTime
    
    @property
    def serverIP(self):
        return self.__ip

    @serverIP.setter
    def serverIP(self, ip:str):
        self.__ip = ip
    
    @property
    def serverPort(self):
        return self.__port

    @serverPort.setter
    def serverPort(self, port:int):
        self.__port = port

    @property
    def serverHeaderLength(self):
        return self.__headerLength

    @serverHeaderLength.setter
    def serverHeaderLength(self, headerLength:int):
        self.__headerLength = headerLength

    def Binding(self):
        self.__socket.bind((self.__ip, self.__port))


if __name__ == "__main__":

    server = BaseSocketServer()
    server.serverHeaderLength = 10
    server.serverIP = '127.0.0.1'
    server.serverPort = 8888
    server.serverIdleTime = 1

    @server.registCommand
    def hello(msg):
        print(msg)

    server.Binding()

    server.run()
import socket
import time
import select
import logging
import os
from datetime import datetime
import sys

class BaseSocketServer(object):
    def __init__(self, ip:str="127.0.0.1", port:int=8050, 
                 headerLength:int=10, idleTime:float=1):
        '''idleTime is in seconds'''
        self.__ip = ip
        self.__port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__headerLength = headerLength
        self.__commandDict = {}
        self.__idleTime = idleTime
        self.__sock_list=[self.__socket]
        self.__clients={}

        
        self.__today_date = datetime.today()
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
        if not os.path.isdir('./Log'): os.mkdir('./Log')
        handler = logging.FileHandler(f'./Log/{self.__today_date.date()}.log')
        handler.setFormatter(formatter)
        self.__logger = logging.getLogger("Server")
        self.__logger.addHandler(handler)
        self.__logger.setLevel(logging.DEBUG)
    
    def __updateHandler(self):
        self.__logger.handlers[0].setStream(open(f'./Log/{datetime.today().date()}.log', 'a'))
    
    def __checkDate(self):
        if self.__today_date != datetime.today().date():
            self.__today_date = datetime.today().date()
            self.__updateHandler()

    def run(self):
        self.__socket.listen()
        self.__logger.info(f"server is working at IP:{self.__ip}, Port:{self.__port}")
        print(f"server is working at IP:{self.__ip}, port:{self.__port}")

        while True:
            self.__checkDate()
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
                
            time.sleep(self.__idleTime)
                # print(notified_socket)
                # print('sleeping....')
                # time.sleep(5)
    def registCommand(self, func):
        self.__commandDict.update({func.__name__:func})
        def wrap(para):
            return func(para)

        return wrap
    
    
    def setLogger(self, logger):
        if isinstance(logger, logging.Logger):
            self.__logger = logger
        else:
            raise TypeError("the logger must be Logger type!")
    
    def addHandler(self, handler):
        if isinstance(handler, logging.Handler):
            self.__logger.addHandler(handler)
        else:
            raise TypeError("handler must be logging.Handler type!")

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
    def IdleTime(self):
        return self.__idleTime
    
    @IdleTime.setter
    def IdleTime(self, idleTime:float):
        "idleTime:seconds"
        self.__idleTime = idleTime
    
    @property
    def IpAddress(self):
        return self.__ip

    @IpAddress.setter
    def IpAddress(self, ip:str):
        self.__ip = ip
    
    @property
    def Port(self):
        return self.__port

    @Port.setter
    def Port(self, port:int):
        self.__port = port

    @property
    def HeaderLength(self):
        return self.__headerLength

    @HeaderLength.setter
    def HeaderLength(self, headerLength:int):
        self.__headerLength = headerLength

    def Binding(self):
        self.__socket.bind((self.__ip, self.__port))


if __name__ == "__main__":

    server = BaseSocketServer()
    server.HeaderLength = 10
    server.IpAddress = '127.0.0.1'
    server.Port = 8888
    server.IdleTime = 1

    @server.registCommand
    def hello(msg):
        print(msg)

    server.Binding()

    server.run()
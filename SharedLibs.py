import socket
from enum import Enum

class IPVersion(Enum):
    Unknown = 0
    IPv4 = 1
    IPv6 = 2

class SockResult(Enum):
    R_Success = 0
    R_GenericError = 1
    ERROR_BufferSizeExceed = 2

class Socket:
    __IPv = IPVersion.Unknown
    __handle = ''
    __MAXPACKETSIZE = 8129 # 8 KB
    __HEADERLENGTH = 4
    
    def __init__(self, IPv = IPVersion.IPv4, socket = ''):
        self.__IPv = IPv
        self.__handle = socket

    def Creat(self):
        if self.__IPv == IPVersion.IPv4:
            addressFamily = socket.AF_INET
        elif self.__IPv == IPVersion.IPv6:
            addressFamily = socket.AF_INET6
        else:
            return SockResult.R_GenericError
        
        self.__handle = socket.socket(addressFamily, socket.SOCK_STREAM)
        return SockResult.R_Success
    
    def Close(self):
        self.__handle.shutdown()
        self.__handle.close()
        return SockResult.R_Success
    
    def Bind(self, ipAddress, port):
        self.__handle.bind((ipAddress, port))
        return SockResult.R_Success

    def Listen(self, backlog):
        self.__handle.listen(backlog)
        return SockResult.R_Success
    
    def Accept(self):
        outSock, sockAddress = self.__handle.accept()
        if outSock.family != socket.AddressFamily.AF_INET:
            return SockResult.R_GenericError
        if len(sockAddress) != 2:
            return SockResult.R_GenericError
        outSock = Socket(socket=outSock)
        return outSock, sockAddress
    
    def Connect(self, ipAddress, port):
        # error = self.__handle.connect_ex((ipAddress, port))
        # # if the server is not available
        # if error != 0:
        #     SockResult.R_GenericError

        self.__handle.connect((ipAddress, port))
        return SockResult.R_Success

    def Send(self, message):
        if len(message) > (self.__MAXPACKETSIZE):
            return SockResult.ERROR_BufferSizeExceed

        ncodedMessage = message.encode("utf-8")
        ncodedSize = len(ncodedMessage)
        
        ncodedHeader = f"{ncodedSize:<{self.__HEADERLENGTH}}".encode("utf-8")

        self.__handle.send(ncodedHeader + ncodedMessage)
        return SockResult.R_Success
    
    def Receive(self):
        try:
            ncodedSize = self.__handle.recv(self.__HEADERLENGTH)
            if not len(ncodedSize):
                return SockResult.R_GenericError

            dcodedSize = int(ncodedSize.decode("utf-8"))
            ncodedMessage = self.__handle.recv(dcodedSize)
            buffer = ncodedMessage.decode("utf-8")
            return buffer
        except:
            return SockResult.R_GenericError

    def SetBlocking(self, BOOL):
        self.__handle.setblocking(BOOL)

    def GetSocket(self):
        return self.__handle

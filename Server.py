#Server Code

from SharedLibs import *
import select

IP = "0.0.0.0"
PORT = 2359

server_socket = Socket(IPVersion.IPv4)
server_socket.Creat()
server_socket.Bind(IP, PORT)
server_socket.Listen(100)
sockets_list = [server_socket.GetSocket()]

clients = {}
buffer = []

print(f"Listening for connections on {IP}:{PORT}...")
    
while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        notified_socket = Socket(IPVersion.IPv4, notified_socket)
        if notified_socket.GetSocket() == server_socket.GetSocket():

            client_socket, client_address = server_socket.Accept()

            user = client_socket.Receive()
            if user == SockResult.R_GenericError:
                continue

            sockets_list.append(client_socket.GetSocket())

            clients[client_socket.GetSocket()] = user

            print("Accepted new connection from {}:{}, username: {}".format(*client_address, user))

            for i in buffer:
                for k, v in i.items():
                    flag = 0
                    if k == user:
                        flag = 1
                    client_socket.Send(str(flag) + ' ' + k + ' ' + v)

        else:
            message = notified_socket.Receive()
            if message == SockResult.R_GenericError:
                print("Closed connection from: {}".format(clients[notified_socket.GetSocket()]))
                sockets_list.remove(notified_socket.GetSocket())
                del clients[notified_socket.GetSocket()]
                continue

            user = clients[notified_socket.GetSocket()]
            if user == SockResult.R_GenericError:
                continue

            buffer.append({user: message})
            print(f"Received message from {user}: {message}")

            for client_socket in clients:

                isSender = 0
                if client_socket == notified_socket.GetSocket():
                    isSender = 1
                    
                tempSocket = Socket(socket=client_socket)
                tempSocket.Send(str(isSender) + ' ' + user + ' ' + message)
        
    for notified_socket in exception_sockets:
        notified_socket = Socket(socket=notified_socket)
        sockets_list.remove(notified_socket.GetSocket())
        del clients[notified_socket.GetSocket()]

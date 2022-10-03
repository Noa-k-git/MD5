import select
import socket
from hashlib import md5

IP='127.0.0.1'
PORT=8822
server_socket = socket.socket()
server_socket.bind((IP, PORT))
print('server is up at : ',IP,PORT)
server_socket.listen(5)
open_client_sockets = []
messages_to_send = []
while True:
   rlist, wlist, xlist = select.select( [server_socket] + open_client_sockets, open_client_sockets, [] )
   for current_socket in rlist:
       if current_socket is server_socket:
           (new_socket, address) = server_socket.accept()
           print("new socket connected to server: ", new_socket.getpeername())
           open_client_sockets.append(new_socket)
       else:
           print ('New data from client!')
           data = current_socket.recv(1024)
           if data == b'end':
               p_id = current_socket.getpeername()
               open_client_sockets.remove(current_socket)
               print (f"Connection with client {p_id} closed.")
               messages_to_send.append((current_socket, data))
           else:
               p_id = current_socket.getpeername()
               print(f"client: {p_id}", data.decode())
               messages_to_send.append((current_socket, b'Hello, ' + data))
   send_waiting_messages(wlist)

def send_waiting_messages(wlist): 
   for message in messages_to_send: 
      current_socket, data = message 
      if current_socket in wlist:     
         current_socket.send(data.encode())  
    messages_to_send.remove(message)


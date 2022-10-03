import socket
import multiprocessing

IP='127.0.0.1'
PORT=8822
my_socket = socket.socket()
my_socket.connect((IP, PORT))
flag=True

cpu_num = multiprocessing.cpu_count()
print(cpu_num)

while flag:
   my_socket.send(cpu_num)
   data = my_socket.recv(1024).decode()
   if data =='end':
       flag=False
   else:
       print ('The server sent: ' + data)
       part, start = int(data.split('-')[0]), int(data.split('-')[1])
       
print('connection to be closed')
my_socket.close()


def generate_num(n):
    yield n + 1
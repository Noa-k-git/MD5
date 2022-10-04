import os
import socket
import multiprocessing
from multiprocessing import Process
from threading import Thread
from hashlib import md5
import time
IP='2a10:8012:11:d55c:e1a6:3202:258a:9651'
PORT=8822
FINISHED_PATH = './finished.txt'
LENGTH = 10

if os.path.exists(FINISHED_PATH) == False:
    with open(FINISHED_PATH, 'w'):
        print("Creating file...")
    print("Done!")

    
def check_nums(hashed, start, count):
    if check_finished():
        return
    
    for n in range(start, start+count+1):
        new_num = '0' * (LENGTH - len(str(n))) + str(n)
        if md5(new_num.encode()).hexdigest() == hashed:
            with open(FINISHED_PATH, 'w') as file:
                file.write(new_num)


def check_finished(path=FINISHED_PATH):
    if os.path.exists(path):
        with open(path, 'r') as f:
           finished = f.read()
        if bool(finished):
            return 'FOUND' + finished
        else:
            return False
    return True 

# def generate_num(n):
#     while True:
#         result = str(n)
#         yield  result + '0' * (LENGTH - len(result))
#         n += 1
        
def listen_finished(my_socket):
    data = my_socket.recv(1024).decode()
    if data[:5] == 'end':
        with open(FINISHED_PATH, 'w') as file:
                file.write('-1')
        
        
if __name__ =="__main__":
    my_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    my_socket.connect((IP, PORT))
    flag=True
    cpu_num = multiprocessing.cpu_count()
    print(cpu_num)

    while flag:
        finished = check_finished()
        if finished and finished[-2:] == '-1':
            break
        elif finished:
            my_socket.send(finished.encode())
            # print('Sending:', finished)
            
        else:
            my_socket.send(str(cpu_num).encode())
        data = my_socket.recv(1024).decode()
        print('\n\ndata:', data)
        if data =='end':
            flag=False
        else:
            print ('The server sent: ' + data)
            # data structure: [startNumber-howManyNumbers-hashedPassword]
            args = data.split('-')
            print(args)
            start, count, hashed = int(args[0]), int(args[1]), args[2]
            
            listen_thread = Process(target=listen_finished, args=(my_socket,), name='Listen')
            listen_thread.start()
            processes = []
            new_start = start
            each = int(count / cpu_num)
            # print("some info", each, count, cpu_num)
            for i in range(1, cpu_num+1):
                processes.append(Process(target=check_nums, args=(hashed, new_start, each), name='pr-'+str(i)))
                new_start += each
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            listen_thread.terminate()
            
    # print('Connection to be closed...', end='\r')
    my_socket.close()
    print('Connection closed!')

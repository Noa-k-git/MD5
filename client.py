import os
import socket
import multiprocessing
from multiprocessing import Process
from threading import Thread
from hashlib import md5

IP='2a10:8012:11:d55c:e1a6:3202:258a:9651'
PORT=8822

LENGTH = 10 # the hashed number length (number of digits)
FINISHED_PATH = './finished.txt' # path to file that indicates wether the number is found, used for communication between the processes.

if os.path.exists(FINISHED_PATH) == False: # creates the file to communicate between the processes
    with open(FINISHED_PATH, 'w'):
        print("Creating file...")
    print("Done!")

    
def check_nums(hashed, start, count):
    """Checks if one of x numbers matches the hashed code.

    Args:
        hashed (string): the hashed code, number to find
        start (int): the function is checking from that number x numbers
        count (int): x numbers to check
    """
    if check_finished():
        return
    
    # only if the number isn't found yet
    for n in range(start, start+count+1):
        new_num = '0' * (LENGTH - len(str(n))) + str(n)
        if md5(new_num.encode()).hexdigest() == hashed:
            with open(FINISHED_PATH, 'w') as file:
                file.write(new_num)


def check_finished(path=FINISHED_PATH):
    """Check the data in the path specified and return wether it has value in it or not.

    Args:
        path (string, optional): The path to the communication file. Defaults to FINISHED_PATH.

    Returns:
        str: whether the number found or not
    """
    if os.path.exists(path):
        with open(path, 'r') as f:
           finished = f.read()
        if bool(finished):
            return 'FOUND' + finished
    return ''
        
def listen_finished(my_socket):
    """Function for listening thread for ending connection with socket.

    Args:
        my_socket (socket.socket): a socket connected to server
    """
    data = my_socket.recv(1024).decode()
    if data[:5] == 'end':
        with open(FINISHED_PATH, 'w') as file:
                file.write('-1')
        
        
if __name__ =="__main__":
    # connect to server
    my_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    my_socket.connect((IP, PORT))
    
    flag=True
    cpu_num = multiprocessing.cpu_count()
    print(cpu_num)

    while flag:
        finished = check_finished()
        if finished and finished[-2:] == '-1': # if received end command from server
            break
        elif finished: # if a process first found the number - sending number to server
            my_socket.send(finished.encode())
            # print('Sending:', finished)
        else: # if number isn't found yet
            my_socket.send(str(cpu_num).encode()) # sending to server cpu number
            
        data = my_socket.recv(1024).decode()
        print('\n\ndata:', data)
        
        if data =='end':
            flag=False
        else:
            print ('The server sent: ' + data)
            # received data structure: [startNumber-howManyNumbers-hashedPassword]
            args = data.split('-')
            print(args)
            start, count, hashed = int(args[0]), int(args[1]), args[2]
            
            listen_thread = Process(target=listen_finished, args=(my_socket,), name='Listen')
            listen_thread.start()
            
            # creating processes for checking numbers
            processes = []
            new_start = start
            each = int(count / cpu_num)

            for i in range(1, cpu_num+1):
                processes.append(Process(target=check_nums, args=(hashed, new_start, each), name='pr-'+str(i)))
                new_start += each
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            listen_thread.terminate()
            
    # print('Connection to be closed...')
    my_socket.close()
    print('Connection closed!')

import select
import socket

IP=' *** IPv6 server address ***'
PORT=8822

# Creating a server
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
server_socket.bind((IP, PORT))
print('server is up at : ',IP,PORT)

server_socket.listen(5)
open_client_sockets = []
messages_to_send = []


tasks = {} # socket:task(bytes)
failed_tasks = [] # all the tasks that clients didn't finish

def send_waiting_messages(wlist):
    """A function for sending messages

    Args:
        wlist (list): sockets to write to.
    """
    for message in messages_to_send: 
        current_socket, data = message 
        if current_socket in wlist:
            try: 
                current_socket.send(data)
                print("Sending data {", data, "}")
            except:
                print("Failed to send data {", data, '}')
        messages_to_send.remove(message)

last_checked = 0 # last number checked
hashed = 'EC9C0F7EDCC18A98B1F31853B1813301'.lower() # the hashed number

each = 1000000 # how many numbers does each cpu gets

while True:
    rlist, wlist, xlist = select.select( [server_socket] + open_client_sockets, open_client_sockets, [])
      
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            print("new socket connected to server: ", new_socket.getpeername())
            open_client_sockets.append(new_socket)
        else:
            try:
                data = current_socket.recv(1024).decode()
                print ('New data from client! {', data, '}')
                
                # informing all client to end connection because the number is already found.
                if data[:5] == 'FOUND':
                    p_id = current_socket.getpeername()
                    for send_socket in wlist:
                        messages_to_send.append((send_socket, b'end'))
                        send_waiting_messages(wlist)
                        send_socket.close()
                        open_client_sockets.remove(send_socket)
                    print (f"Connection with client {p_id} closed.")
                    print('---'*6 + '\nNumber found:\n' + data[5:] + '\n' + '---'*6)

                else:
                    # sending new tasks for clients
                    p_id = current_socket.getpeername()
                    print(f"client: {p_id}", data)
                    if failed_tasks != []: # if there are tasks that failed resending them to clients
                        tasks[current_socket] = failed_tasks[0]
                        del failed_tasks[0]
                        print("Failed Tasks:", failed_tasks)
                    else: # sending new number to check
                        amount_to_check = each*int(data)
                        tasks[current_socket] = (str(last_checked) + '-' + str(amount_to_check) + '-' + hashed).encode()
                        last_checked += amount_to_check
                        
                    print(tasks[current_socket])
                    messages_to_send.append((current_socket, tasks[current_socket]))
                    
            except ConnectionResetError: # handling a client randomly closed
                print("Socket forcibly closed! ConnectionResetError")
                
                failed_tasks.append(tasks[current_socket])
                print("Failed Tasks:", failed_tasks)
                del tasks[current_socket]
                open_client_sockets.remove(current_socket)
    send_waiting_messages(wlist)

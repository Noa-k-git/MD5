import select
import socket
IP='2a10:8012:11:d55c:e1a6:3202:258a:9651'

PORT=8822
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
server_socket.bind((IP, PORT))
print('server is up at : ',IP,PORT)
server_socket.listen(5)
open_client_sockets = []
messages_to_send = []


tasks = {}
failed_tasks = [] #[[start, numAfter], [,]]
def send_waiting_messages(wlist): 
    for message in messages_to_send: 
        current_socket, data = message 
        if current_socket in wlist:
            try: 
                current_socket.send(data)
                print("Sending data {", data, "}")
            except:
                print("Failed to send data {", data, '}')
        messages_to_send.remove(message)
        
# def get_task(cpu_num, last, hashed):
#     global failed_tasks
#     each = 100000
#     if failed_tasks != []:
#         task = failed_tasks[0]
#         failed_tasks = failed_tasks[1:]
#         return task
#     else:
#         print(str(cpu_num))
#         return (str(last) + '-' + str(each*cpu_num) + '-' + hashed).encode()
        
last_checked = 0
hashed = 'EC9C0F7EDCC18A98B1F31853B1813301'.lower()

each = 1000000

while True:
    rlist, wlist, xlist = select.select( [server_socket] + open_client_sockets, open_client_sockets, [] )
    # for current_socket in wlist:
        # try:
        #     current_socket.getpeername()
        # except OSError:
        #     print("Socket forcibly closed! OSError")
        #     failed_tasks.append(tasks[current_socket])
        #     del tasks[current_socket]
        #     open_client_sockets.remove(current_socket)
            
    for current_socket in rlist:
        
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            print("new socket connected to server: ", new_socket.getpeername())
            open_client_sockets.append(new_socket)
        else:
            try:
                data = current_socket.recv(1024).decode()
                print ('New data from client! {', data, '}')
                
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
                    p_id = current_socket.getpeername()
                    print(f"client: {p_id}", data)
                    if failed_tasks != []:
                        tasks[current_socket] = failed_tasks[0]
                        del failed_tasks[0]
                        print("Failed Tasks:", failed_tasks)
                    else:
                        amount_to_check = each*int(data)
                        tasks[current_socket] = (str(last_checked) + '-' + str(amount_to_check) + '-' + hashed).encode()
                        last_checked += amount_to_check
                    print(tasks[current_socket])
                    messages_to_send.append((current_socket, tasks[current_socket]))
            except ConnectionResetError:
                print("Socket forcibly closed! ConnectionResetError")
                
                failed_tasks.append(tasks[current_socket])
                print("Failed Tasks:", failed_tasks)
                del tasks[current_socket]
                open_client_sockets.remove(current_socket)
    send_waiting_messages(wlist)

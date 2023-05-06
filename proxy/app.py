import random
import socket
import threading

import art

LHOST = "127.0.0.1"  # Standard loopback interface address (localhost)
LPORT = 5500  # Port to listen on (non-privileged ports are > 1023)

CHOST = "app"
CPORT = 5000


listen_socket = socket.create_server((LHOST, LPORT))
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def handle_connection(conn, addr):
    print(f'[INFO] Connection from {addr[0]}:{addr[1]}')
    random_num1 = random.randint(0, 10)
    random_num2 = random.randint(0, 10)
    random_operation = random.choice(['+', '-', 'x'])
    correct_answer = None
    if random_operation == '+':
        correct_answer = random_num1 + random_num2
    elif random_operation == '-':
        correct_answer = random_num1 - random_num2
    elif random_operation == 'x':
        correct_answer = random_num1 * random_num2

    t = art.text2art(f'{random_num1} {random_operation} {random_num2}= ?')
    conn.sendall(t.encode()+b'\n\n')

    answer = conn.recv(1024).decode()
    if not answer:
        print('answer not received')
        conn.close()
        return

    if int(answer) != correct_answer:
        conn.sendall(b'Wrong answer. Closing connection\n')
        conn.close()
        return
    else:
        conn.sendall(b'Captcha solved. Please commence HTTP\n')

    try:
        d = b""
        while True:
            data = conn.recv(10240)
            if not data or data == b'\r\n' or data == b'\n':
                if 'Content-Length' in d.decode():
                    # find Content-Length's position
                    pos = d.find(b'Content-Length')
                    # find the end of the line
                    end = d.find(b'\r\n', pos)
                    # find the value of Content-Length
                    length = int(d[pos + 15:end])
                    # check if the body length is equal to the value of Content-Length
                    blength = len(d[end + 2:])
                    if blength == length + 4:
                        break
                else:
                    break
            d += data
        http_socket = socket.create_connection((CHOST, CPORT))
        http_socket.sendall(d + b'\r\n')
        res = http_socket.recv(10240, socket.MSG_WAITALL)


        if not d:
            print('data not received from http_socket')
        
        conn.sendall(res + b'\r\n')
        print(f'[INFO] Connection from {addr[0]}:{addr[1]} closed')
        http_socket.close()
        conn.close()
    except Exception as e:
        print(f'[INFO] Connection from {addr[0]}:{addr[1]} closed with error: {e}')
        conn.close()

if __name__ == '__main__':
    listen_socket.listen()
    print(f'[INFO] Listening on {LHOST}:{LPORT}')
    while True:
        conn, addr = listen_socket.accept()
        t = threading.Thread(target=handle_connection, args=(conn, addr))
        t.start()

        
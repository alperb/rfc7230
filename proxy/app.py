import random
import socket

import art

LHOST = "127.0.0.1"  # Standard loopback interface address (localhost)
LPORT = 5500  # Port to listen on (non-privileged ports are > 1023)

CHOST = "127.0.0.1"
CPORT = 5000


listen_socket = socket.create_server((LHOST, LPORT))
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

while True:
    listen_socket.listen()
    print(f'[INFO] Listening on {LHOST}:{LPORT}')
    conn, addr = listen_socket.accept()
    print(f'[INFO] Connection from {addr[0]}:{addr[1]}')
    with conn:
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
            continue

        if int(answer) != correct_answer:
            conn.sendall(b'Wrong answer. Closing connection\n')
            conn.close()
            continue
        else:
            conn.sendall(b'Captcha solved. Please commence HTTP\n')

        try:
            d = b""
            while True:
                data = conn.recv(10240)
                if not data or data == b'\r\n':
                    if 'Content-Length' in d.decode():
                        # find Content-Length's position
                        pos = d.find(b'Content-Length')
                        # find the end of the line
                        end = d.find(b'\r\n', pos)
                        # find the value of Content-Length
                        length = int(d[pos + 15:end])
                        # check if the body length is equal to the value of Content-Length
                        blength = len(d[end + 2:])
                        print(f'blength: {blength}')
                        print(f'length: {length}')
                        if blength == length + 4:
                            break
                    else:
                        break
                print(f'data: {data}')
                d += data
            print(f'd: {d}')
            http_socket = socket.create_connection((CHOST, CPORT))
            http_socket.sendall(d + b'\r\n')
            res = http_socket.recv(10240, socket.MSG_WAITALL)


            if not d:
                print('data not received from http_socket')
            
            conn.sendall(res + b'\r\n')
        except Exception as e:
            print(f'error with peer: {e}')
            conn.close()
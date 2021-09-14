from logging import error
import socket
from datetime import datetime
import json

class UDPClient:
    ''' A simple UDP Client that uses IPv4 '''

    def __init__(self):
        self.conn_sock = None   # connection socket

    def printwt(self, msg):
        ''' Print message with current date and time '''
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}] {msg}')

    def create_socket(self):
        ''' Create a socket that uses IPv4 and UDP '''
        self.printwt('1 Creating connection socket ...')
        self.conn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.printwt('Socket created')

    def interact_with_server(self, host, port, data_dic):
        ''' Connect and interact with a UDP Server. '''
        self.host = host        # host address
        self.port = port        # host port
        try:
            msg = json.dumps(data_dic)
            self.conn_sock.sendto(bytes(msg, "utf-8"), (self.host,self.port))
            self.printwt(f'[ SENT ] {msg} \n')
            retMsg = str(self.conn_sock.recv(1024),"utf-8")
            with open(f"./json/{host}.json", "w") as f:
                json.dump(retMsg, f)
        except OSError as err:
            self.printwt('Cannot connect to server')
            print(err)

def main():
    ''' Create a UDP Client and interact with the server at 127.0.0.1:4444'''

    tcp_client = UDPClient()
    tcp_client.create_socket()
    GPIOOUT = [65, 68, 70, 71, 72, 73, 74, 76]
    GPIOIN = [111, 112, 113, 114, 229, 117, 118, 75]
    k = 1
    for i, o in zip(GPIOIN,GPIOOUT):
        data_dic={"GPIO_IN": i, "GPIO_OUT": o,"data": f"{k}.mp4"}
        k += 1
        tcp_client.interact_with_server('192.168.0.27', 8080, data_dic=data_dic)


if __name__ == '__main__':
    main()
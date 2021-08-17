from logging import error
import socket
from datetime import datetime
import json

class UDPClient:
    ''' A simple UDP Client that uses IPv4 '''

    def __init__(self, host, port):
        self.host = host        # host address
        self.port = port        # host port
        self.conn_sock = None   # connection socket

    def printwt(self, msg):
        ''' Print message with current date and time '''

        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}] {msg}')

    def create_socket(self):
        ''' Create a socket that uses IPv4 and UDP '''

        self.printwt('Creating connection socket ...')
        self.conn_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.printwt('Socket created')

    def interact_with_server(self, data_dic=None):
        ''' Connect and interact with a UDP Server. '''
        try:
            msg = json.dumps(data_dic)
            self.conn_sock.sendto(bytes(msg, "utf-8"), (self.host,self.port))
            self.printwt('[ SENT ]')
            print('\n', msg, '\n')
        except OSError as err:
            self.printwt('Cannot connect to server')
            print(err)

def main():
    ''' Create a UDP Client and interact with the server at 127.0.0.1:4444'''

    tcp_client = UDPClient('127.0.0.1', 8080)
    tcp_client.create_socket()
    tcp_client.interact_with_server(data_dic={"GPIO_IN": 65, "GPIO_OUT": 111,"data": "video.mp4"})


if __name__ == '__main__':
    main()
from datetime import datetime
import socket
import json
import yaml
from argparse import ArgumentParser
import logging.config
# import hashlib
# import zlib
import threading
import asyncio
from getpass import getpass

parser = ArgumentParser()
parser.add_argument(
    '-c', '--config', type=str,
    required=False,
    help='Sets run configuration file'
)

parser.add_argument(
    '-m','--mode', type=str, default='w',
    help='Sets client mode'
)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('client')

host = 'localhost'
port = 8000
buffersize = 1024
encoding = 'utf-8'

args = parser.parse_args()

if args.config:
    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')


class Client():
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        logger.info('Client started')
        # self.ioloop = asyncio.get_event_loop()
        code = None
        while code != 200:
            self.login, self.password = self.init()
            code, data = self.connect_to_server(self.password)
            if code == 200:
                continue
            else:
                print(data+' - '+str(code))
        self.responses = []
        self.main_loop()
        # wait_tasks = asyncio.wait([self.main_loop()])
        # self.ioloop.run_until_complete(wait_tasks)

    def read(self):
        while True:
            b_response = self.sock.recv(buffersize)
            response = b_response.decode(encoding)
            # b_response = zlib.decompressobj().decompress(response)
            if response:
                logger.info(f'Получен ответ: {response}')
                self.responses.append(response)

    def send_to_server(self, action, data):
        request = {
            'action': action,
            'data': data,
            'time': datetime.now().timestamp(),
            'user': self.login
        }
        logger.info(f'{request}')
        s_request = json.dumps(request)
        self.sock.send(s_request.encode(encoding))

    def write(self):
        while True:
            action = 'echo'
            # action = input('Enter action: ')
            data = input('Enter data: ')
            # hash_obj = hashlib.sha256()
            # hash_obj.update(
            #     (str(datetime.now().timestamp()).encode(encoding))
            # )
            if data:
                self.send_to_server(action, data)
            else:
                # self.send_to_server('get_messages', data)
                while self.responses:
                    response = self.responses.pop()
                    print(response)

    def main_loop(self):
        if args.mode == 'w':
            # ioloop.create_task(write)
            self.write()
        elif args.mode == 'rw':
            # self.ioloop.create_task(self.write)
            wthread = threading.Thread(target=self.write, daemon=True)
            wthread.start()
            self.read()
            # rthread = threading.Thread(target=self.read, daemon=True)
            # rthread.start()
        else:
            # ioloop.create_task(read())
            self.read()

    def connect_to_server(self, password):
        self.send_to_server('login', password)
        response = None
        while not response:
            response = self.sock.recv(buffersize)
        s_response = json.loads(response.decode(encoding))
        return s_response['code'], s_response['data']

    @staticmethod
    def init():
        login = input("Login: ")
        password = getpass("Password: ")
        return login, password


try:
    client = Client()
except KeyboardInterrupt:
    pass
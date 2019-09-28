from argparse import ArgumentParser
import logging.config
import yaml, json
from handlers import handle_default_request
from DB import Connect
import socket
from select import select
import asyncio
import time
import threading

parser = ArgumentParser()
parser.add_argument(
    '-c', '--config', type=str,
    required=False,
    help='Sets run configuration file'
)

args = parser.parse_args()

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('server')


class Server(object):
    def __init__(self):
        self.host, self.port = None, None
        config_file = 'client/config.yml'
        if args.config:
            config_file = args.config
        try:
            with open(config_file) as file:
                config = yaml.load(file, Loader=yaml.Loader)
                self.host = config.get('host')
                self.port = config.get('port')
                logging.info(f'Set parameters from config file for host:port of server - {self.host}:{self.port}')
        except FileNotFoundError:
            self.host = '0.0.0.0'
            self.port = 8000
            logging.info(f'Set default parameters for host:port of server - {self.host}:{self.port}')

        self.buffersize = 1024
        self.encoding = 'utf-8'
        self.connections = []
        self.requests = []
        self.clients = {}
        self.conn = Connect()
        self.ioloop = asyncio.get_event_loop()

    def __del__(self):
        self.ioloop.close()
        del self.conn

    def disconnect(self, client):
        logging.info(f'Client {client.getpeername()} with name {self.clients.get(client)} disconnected')
        try:
            self.clients.pop(client)
        except KeyError:
            # нет клиента для удаления
            logger.debug(f"Don't exist client {client.getpeername()} in dict clients")
            for key, value in self.clients.items():
                print(key.getpeername(), value)
        self.connections.remove(client)

    def check_connection(self, client):
        if client in self.clients:
            connection_exists = True
        else:
            self.disconnect(client)
            connection_exists = False
        return connection_exists

    def read(self, client):
        try:
            b_request = client.recv(self.buffersize)
            if b_request != b'' and b_request is not None:
                logger.debug(f'Request {b_request} from client {client.getpeername()}')

                request = json.loads(b_request.decode(self.encoding))
                if request["action"] == 'login':
                    b_response = handle_default_request(b_request)
                    response = json.loads(b_response.decode(self.encoding))
                    if response["code"] == 200:
                        self.clients.update({client: request["user"]})
                    client.send(b_response)
                else:
                    self.requests.append(b_request)
        except ConnectionResetError:
            self.disconnect(client)

    def write(self, client, b_response):
        if self.check_connection(client) and b_response != b'' and b_response is not None:
            logger.debug(f'Response {b_response} send to client {client.getpeername()} with name {self.clients.get(client)}')
            client.send(b_response)
            self.conn.send_message(self.clients[client], json.loads(b_response.decode(self.encoding)))

    def listen_connections(self):
        sock = socket.socket()
        try:
            sock.bind((self.host, self.port))
            sock.setblocking(False)
            sock.listen(5)
            logger.info(f'Server was started with {self.host}:{self.port}')
            while True:
                try:
                    client, address = sock.accept()
                    logger.info(f'Client with address {address} was detected')
                    self.connections.append(client)
                except BlockingIOError:
                    # исключение происходит когда нет ни одного соединения
                    time.sleep(0.1)
                    # logger.debug('Don\'t exist new connections')
        finally:
            sock.close()

    def listen_events(self):
        while True:
            try:
                rlist, wlist, xlist = select(self.connections, self.connections, self.connections, 1)
            except OSError:
                pass
                # исключение происходит когда нет ни одного соединения
                time.sleep(0.1)
                # logger.debug('Don\'t exist any connections')
            else:
                for r_client in rlist:
                    self.ioloop.create_task(self.read(r_client))
                    # threading.Thread(target=self.read, args=r_client).start()

                while self.requests:
                    b_request = self.requests.pop()
                    b_response = handle_default_request(b_request)

                    for w_client in wlist:
                        self.ioloop.create_task(self.write(w_client, b_response))
                        # threading.Thread(target=self.write, args=(w_client, b_response)).start()

    def start(self):
        threading.Thread(target=self.listen_connections, daemon=True).start()
        wait_task = asyncio.wait([self.listen_events()])
        self.ioloop.run_until_complete(wait_task)


if __name__ == '__main__':
    try:
        Server().start()
    except KeyboardInterrupt:
        pass

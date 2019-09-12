import socket
import yaml, json
import time
from argparse import ArgumentParser
from handlers import handle_default_request
import logging.config
from select import select
# import threading
import asyncio
from DB import Connect

parser = ArgumentParser()
parser.add_argument(
    '-c', '--config', type=str,
    required=False,
    help='Sets run configuration file'
)

args = parser.parse_args()

host = '0.0.0.0'
port = 8000
buffersize = 1024
encoding = 'utf-8'

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('server')

if args.config:
    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')

connections = []
requests = []
conn = Connect()
clients = {}


def read(client):
    b_request = client.recv(buffersize)
    logger.debug(f'request {b_request} from client {client.getpeername()}')

    request = json.loads(b_request.decode(encoding))
    if request["action"] == 'login':
        b_response = handle_default_request(b_request)
        response = json.loads(b_response.decode(encoding))
        if response["code"] == 200:
            clients.update({client: request["user"]})
            for key, value in clients.items():
                print(key.getpeername(), value)
        client.send(b_response)
    else:
        requests.append(b_request)


def write(client, b_response):
    logger.debug(f'response {b_response} send to client {client.getpeername()} with name {clients.get(client)}')
    client.send(b_response)
    conn.send_message(clients[client], json.loads(b_response.decode(encoding)))


def main_loop():
    sock = socket.socket()
    sock.bind((host, port))
    sock.setblocking(False)
    # sock.settimeout(1)
    sock.listen(5)

    logger.info(f'Server was started with {host}:{port}')
    time.sleep(10)

    while True:
        try:
            client, address = sock.accept()
            logger.info(f'Client with address {address} was detected.')
            connections.append(client)
        except:
            pass

        rlist, wlist, xlist = select(connections, connections, connections, 0)

        for r_client in rlist:
            ioloop.create_task(read(r_client))
            # rthread = threading.Thread(target=read, args=(r_client))
            # rthread.start()

        while requests:
            b_request = requests.pop()
            b_response = handle_default_request(b_request)

            for w_client in wlist:
                ioloop.create_task(write(w_client, b_response))
                # wthread = threading.Thread(target=write, args=(w_client, b_response))
                # wthread.start()


ioloop = asyncio.get_event_loop()
try:
    wait_tasks = asyncio.wait([main_loop()])
    ioloop.run_until_complete(wait_tasks)
except KeyboardInterrupt:
    pass
finally:
    ioloop.close()

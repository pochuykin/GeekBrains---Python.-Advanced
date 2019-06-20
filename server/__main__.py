import socket
import yaml
import time
from argparse import ArgumentParser
from handlers import handle_default_request
import logging.config
from select import select

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

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('.\main.log', encoding=encoding)
#         , logging.StreamHandler()
#     ]
# )
logging.config.fileConfig('logging.conf')

logger = logging.getLogger('server')

if args.config:
    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')

connections = []
requests = []

try:
    sock = socket.socket()

    sock.bind((host, port))
    sock.setblocking(False)
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
            b_request = r_client.recv(buffersize)
            logger.debug(f'request {b_request} from client {r_client} added to list')
            requests.append(b_request)

        while requests:
            b_request = requests.pop()
            b_response = handle_default_request(b_request)

            for w_client in wlist:
                logger.debug(f'response {b_response} send to client {w_client}')
                w_client.send(b_response)
except KeyboardInterrupt:
    pass

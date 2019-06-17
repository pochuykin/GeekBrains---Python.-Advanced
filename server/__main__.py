import socket
import yaml
from argparse import ArgumentParser
from handlers import handle_default_request
import logging

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

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.\main.log', encoding=encoding),
        logging.StreamHandler()
    ]
)

if args.config:
    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')

try:
    sock = socket.socket()

    sock.bind((host, port))
    sock.listen(5)
    logging.info(f'Server was started with {host}:{port}')

    while True:
        client, address = sock.accept()

        b_request = client.recv(buffersize)
        b_response = handle_default_request(b_request)
        client.send(b_response)
        client.close()

except KeyboardInterrupt:
    pass

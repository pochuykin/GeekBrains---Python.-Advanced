from datetime import datetime
import socket
import json
import yaml
from argparse import ArgumentParser
import logging.config
import hashlib
import zlib
import threading

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

args = parser.parse_args()

host = 'localhost'
port = 8000
buffersize = 1024
encoding = 'utf-8'

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('client')


def read():
    while True:
        response = sock.recv(buffersize)
        # b_response = zlib.decompressobj().decompress(response)
        if response:
            logger.info(f'Получен ответ: {response.decode(encoding)}')

def write():
    while True:
        action = input('Enter action: ')
        data = input('Enter data: ')
        hash_obj = hashlib.sha256()
        hash_obj.update(
            (str(datetime.now().timestamp()).encode(encoding))
        )

        request = {
            'action': action,
            'data': data,
            'time': datetime.now().timestamp(),
            'user': hash_obj.hexdigest()
        }
        s_request = json.dumps(request)
        logger.info(f'{request}')
        sock.send(s_request.encode(encoding))


if args.config:
    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')


try:
    sock = socket.socket()
    sock.connect((host, port))
    logger.info('Client started')

    if args.mode == 'w':
        write()
    elif args.mode == 'rw':
        rthread = threading.Thread(target=read, daemon=True)
        rthread.start()
        write()
    else:
        read()
except KeyboardInterrupt:
    pass
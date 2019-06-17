from datetime import datetime
import socket
import json
import yaml
from argparse import ArgumentParser
import logging
import hashlib

parser = ArgumentParser()
parser.add_argument(
    '-c', '--config', type=str,
    required=False,
    help='Sets run configuration file'
)

args = parser.parse_args()

host = 'localhost'
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
    sock.connect((host, port))
    logging.info('Client started')
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
    logging.info(f'{request}')
    sock.send(s_request.encode(encoding))
    response = sock.recv(buffersize)
    logging.info(f'Получен ответ: {response.decode(encoding)}')
except KeyboardInterrupt:
    pass
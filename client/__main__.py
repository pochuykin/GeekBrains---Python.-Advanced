from datetime import datetime
import socket
import json
import yaml
from argparse import ArgumentParser
import logging

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

logger = logging.getLogger('main')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('.\main.log', encoding='UTF-8')

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

if args.config:
    with open(args.config) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')

try:
    sock = socket.socket()
    sock.connect((host, port))
    logger.info('Client started')
    action = input('Enter action: ')
    data = input('Enter data: ')
    request = {
        'action': action,
        'data': data,
        'time': datetime.now().timestamp()
    }
    s_request = json.dumps(request)
    logger.info(f'{request}')
    sock.send(s_request.encode(encoding))
    response = sock.recv(buffersize)
    logger.info(f'Получен ответ: {response.decode(encoding)}')
except KeyboardInterrupt:
    pass
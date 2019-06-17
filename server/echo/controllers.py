from protocol import make_response
import logging

logger = logging.getLogger('main')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('.\main.log', encoding='UTF-8')

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def get_echo(request):
    logger.info('get_echo launch')
    data = request.get('data')
    return  make_response(request, 200, data)
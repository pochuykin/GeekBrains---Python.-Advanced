from datetime import datetime
import logging


logger = logging.getLogger('main')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('.\main.log', encoding='UTF-8')

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def validate_request(raw):
    logger.info('validate_request launch')
    request_time = raw.get('time')
    request_action = raw.get('action')

    return request_action and request_time


def make_response(request, code, data=None):
    logger.info('make_response launch')
    return {
        'action': request.get('action'),
        'user': request.get('user'),
        'time': datetime.now().timestamp(),
        'data': data,
        'code': code
    }
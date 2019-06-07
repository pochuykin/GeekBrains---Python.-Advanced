from datetime import datetime


def validate_request(raw):
    request_time = raw.get('time')
    request_action = raw.get('action')

    return request_action and request_time


def make_response(request, code, data=None):
    return {
        'action': request.get('action'),
        'user': request.get('user'),
        'time': datetime.now().timestamp(),
        'data': data,
        'code': code
    }
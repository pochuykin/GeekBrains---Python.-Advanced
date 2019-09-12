import logging
from functools import wraps
from protocol import make_response
from inspect import stack

logger = logging.getLogger('decorators')


def log(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        logger.debug(f'{stack()[1][3]} called {func.__name__} : {request}')
        return func(request, *args, **kwargs)
    return wrapper


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        print('login_required' + request.decode())
        if 'user' in request.decode():
            return func(request, *args, **kwargs)
        return make_response(request, 403, 'Access denied')
    return wrapper

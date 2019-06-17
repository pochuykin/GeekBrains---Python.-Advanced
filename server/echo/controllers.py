from protocol import make_response
from decorators import log


@log
def get_echo(request):
    data = request.get('data')
    return make_response(request, 200, data)


from protocol import make_response
from decorators import log
from DB import Connect

@log
def login(request):
    login = request['user']
    password = request.get('data')
    conn = Connect()
    # проверяем пароль, и устанавливаем указанный, если пароля еще нет
    if conn.check_password(login, password):
        code, data = (200, None)
    else:
        code, data = (403, 'Access denied')
    return make_response(request, code, data)




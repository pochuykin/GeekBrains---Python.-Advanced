from datetime import datetime
import socket
import json
import yaml
from argparse import ArgumentParser
import logging.config
import threading
import asyncio
from getpass import getpass

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

# parser = ArgumentParser()
# parser.add_argument(
#     '-c', '--config', type=str,
#     required=False,
#     help='Sets run configuration file'
# )
#
# parser.add_argument(
#     '-u', '--user', type=str, default='1',
#     help='Set login'
# )
#
# parser.add_argument(
#     '-p', '--password', type=str, default='1',
#     help='Set password'
# )
#
# args = parser.parse_args()

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('client')

host, port = None, None
buffersize = 1024
encoding = 'utf-8'


config_file = 'client/config.yml'
# if args.config:
#     config_file = args.config
try:
    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.Loader)
        host = config.get('host')
        port = config.get('port')
except FileNotFoundError:
    host = 'localhost'
    port = 8000


class Client(object):
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        logger.info(f'Client started with address {host}:{port}')
        self.responses = []
        self.login, self.password = '', ''# args.user, args.password

    def try_login(self):
        code = None
        while code != 200:
            self.login, self.password = self.init()
            code, data = self.connect_to_server()
            if code != 200:
                logger.info('Not connected: '+data+' - '+str(code))

    @staticmethod
    def init():
        login = input("Login: ")
        password = getpass("Password: ")
        return login, password

    def connect_to_server(self):
        self.send_to_server('login', self.password)
        response = None
        while not response:
            response = self.sock.recv(buffersize)
        s_response = json.loads(response.decode(encoding))
        return s_response['code'], s_response['data']

    def start(self):
        self.try_login()
        threading.Thread(target=self.write, daemon=True).start()
        self.read()

    def read(self):
        while True:
            b_response = self.sock.recv(buffersize)
            response = b_response.decode(encoding)
            s_response = json.loads(response)
            if response:
                logger.info(f'Получен ответ: {response}')
                app.chat_screen.chat.text = f'{app.chat_screen.chat.text} \n {s_response["user"]} : {s_response["data"]}'
                self.responses.append(response)

    def write(self):
        while True:
            action = 'echo'
            data = input('Enter data: ')
            if data:
                self.send_to_server(action, data)
            else:
                # self.send_to_server('get_messages', data)
                while self.responses:
                    response = self.responses.pop(0)
                    print(response)

    def send_to_server(self, action, data):
        request = {
            'action': action,
            'data': data,
            'time': datetime.now().timestamp(),
            'user': self.login
        }
        logger.info(f'{request}')
        s_request = json.dumps(request)
        self.sock.send(s_request.encode(encoding))


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        login_layout = GridLayout()
        login_layout.cols = 2
        login_layout.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False, text=client.login)
        login_layout.add_widget(self.username)
        login_layout.add_widget(Label(text='Password'))
        self.password = TextInput(password=True, multiline=False, text=client.password)
        login_layout.add_widget(self.password)
        login_btn = Button(text="Login")
        login_btn.bind(on_press=self.try_login)
        login_layout.add_widget(login_btn)
        registry_btn = Button(text="Registry")
        registry_btn.bind(on_press=self.try_registration)
        login_layout.add_widget(registry_btn)
        # self.username.text = "1"
        # self.password.text = "1"
        self.add_widget(login_layout)

    def changer(self, *args):
        self.manager.current = 'chat_screen'

    def try_login(self, *args):
        client.login, client.password = self.username.text, self.password.text
        code, data = client.connect_to_server()
        if code != 200:
            logger.info('Not connected: '+data+' - '+str(code))
        else:
            self.changer()
            threading.Thread(target=client.read, daemon=True).start()

    def try_registration(self, *args):
        self.try_login()


class ChatScreen(Screen):

    def __init__(self, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical')
        self.chat = Label()
        self.chat.height = 20
        main_layout.add_widget(self.chat)

        input_layout = BoxLayout(orientation='horizontal')
        self.text_editor = TextInput()
        input_layout.add_widget(self.text_editor)
        self.send_button = Button(text="Send")
        self.send_button.bind(on_press=self.send_to_server)
        input_layout.add_widget(self.send_button)

        main_layout.add_widget(input_layout)
        self.add_widget(main_layout)

    def send_to_server(self, *args):
        default_action = 'echo'
        client.send_to_server(default_action, self.text_editor.text)
        self.text_editor.text = ''


class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_screen = ChatScreen(name='chat_screen')
        self.login_screen = LoginScreen(name='login_screen')

    def build(self):
        sm = ScreenManager()
        sm.add_widget(self.login_screen)
        sm.add_widget(self.chat_screen)
        return sm


if __name__ == '__main__':
    client = None
    try:
        client = Client()
        app = MyApp()
        app.run()
        # client.start()
    except KeyboardInterrupt:
        pass
    finally:
        del client

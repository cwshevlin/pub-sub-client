import socket
import time
import json
from locust import task, User, between

HOST = 'http://localhost:8080/'
PORT = 8080

class WebSocketClient:
    def


class WebSocketUser(User):
    abstract = True

    def connect(self, host: str, header: list):
        # TODO CWS: create a connection here and spawn a gevent

        # This may need reformatting of the address
        self.socket = socket.connect((HOST, PORT))

    def on_message(self, message):
        # Time the message and return the time
        current_timestamp = time.time()
        # fire a request event in the environment: https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/users/socketio.py#L72

    def receive_loop(self):
        # receive data: https://docs.python.org/3/library/socket.html#socket.socket.recv
        while True:
            message = self.ws.recv()
            logging.debug(f"WSR: {message}")
            self.on_message(message)
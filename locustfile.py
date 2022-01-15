import socket
import time
import json
from locust import task, User, between
import gevent
import logging

HOST = 'localhost'
PORT = 8080
BUF_SIZE = 128

class WebSocketUser(User):
    abstract = True

    def connect(self, host: str, header: list=None):
        # This may need reformatting of the address
        gevent.spawn(self.receive_loop)

    def on_message(self, message):
        # Time the message and return the time
        current_timestamp = time.time()
        
        # Parse message body to get the timestamp
        name = "socket send"
        response_time = current_timestamp - time.time()

        # send an event that we recieved a message
        self.environment.events.request.fire(
            request_type="rx",
            name=name,
            response_time=response_time,
            response_length=len(message),
            exception=None,
            context=self.context(),
        )

    def receive_loop(self):
        # receive data: https://docs.python.org/3/library/socket.html#socket.socket.recv
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                message = b"Hello work client"
                s.connect((HOST, PORT))
                s.sendall(message)
                message = s.recv(BUF_SIZE)
                logging.debug(f"Recieved: {message} on socket {s}")
                self.on_message(message)

    def send(self, body, name=None, context={}):
        # https://github.com/SvenskaSpel/locust-plugins/blob/master/locust_plugins/users/socketio.py#L102
        self.socket.sendall(body)

        self.environment.events.request.fire(
            request_type="tx",
            name=name,
            response_time=None,
            response_length=len(body),
            exception=None,
            context={**self.context(), **context},
        )

class SimpleWebSocketWriter(WebSocketUser):
    @task
    def task(self):
        self.value = None
        self.connect('localhost:8080')

        while not self.value:
            time.sleep(0.1)

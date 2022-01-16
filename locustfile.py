import socket
import time
import json
from locust import task, User, between
import gevent
import logging

HOST = 'localhost'
PORT = 8080
BUF_SIZE = 64

class WebSocketUser(User):
    abstract = True

    def connect(self, host: str, header: list=None):
        # This may need reformatting of the address
        gevent.spawn(self.receive_loop)

    def context(self):
        return {}

    def on_message(self, message):
        # Time the message and return the time
        current_timestamp = time.time()
        
        # Parse message body to get the timestamp
        name = "roundtrip"
        message = str(message, "utf-8").strip("\x00")
        print(repr(message))
        message = json.loads(message)
        sent_at = message["sent_at"]
        response_time = current_timestamp - sent_at
        print(response_time)

        # send an event that we recieved a message
        self.environment.events.request.fire(
            request_type="SOCKET",
            name=name,
            response_time=response_time,
            response_length=len(message),
            exception=None,
            context=self.context()
        )

    def receive_loop(self):
        # receive data: https://docs.python.org/3/library/socket.html#socket.socket.recv
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                body = {
                    "sent_at": time.time()
                }
                message = json.dumps(body, indent=2).encode('utf-8')
                s.connect((HOST, PORT))
                s.sendall(message)
                name = "roundtrip"

                self.environment.events.request.fire(
                    request_type="SOCKET",
                    name=name,
                    response_time=None,
                    response_length=len(body),
                    exception=None,
                    context=self.context(),
                )

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

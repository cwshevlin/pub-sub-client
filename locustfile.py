import socket
import time
import json
from locust import task, HttpUser, between
import gevent
import logging

HOST = 'localhost'
PORT = 8080
BUF_SIZE = 64

class WebSocketUser(HttpUser):
    abstract = True

    def connect(self, url: str, header: list=None):
        # This may need reformatting of the address
        gevent.spawn(self.receive_loop(url))

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

    def receive_loop(self, url):
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
    wait_time = between(10, 300)
    host = "http://localhost:8000"

    @task
    def connect(self):
        # Make a request to the register endpoint
        register_result = self.client.get("/register")
        print(register_result)
        print(f"response body: {register_result.json()}")
        ws_url = register_result.json()["url"]
        self.host = "http://127.0.0.1:8000/"
        self.client.base_url = "ws://127.0.0.1:8000/"
        path = ws_url[20:] # TODO CWS: magic number
        print(f"PATH: {path}")
        
        # # Send an upgrade request to the ws endpoint
        response = self.client.request("GET", path, headers={
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Key": "JsuW3srSODh+N6kyxu7WzQ==",
            "Connection": "Upgrade",
            "Upgrade": "websocket",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Host": "127.0.0.1:8000",
        })
        # TODO: create a transport adapter, or just use the socket library above??
        # https://docs.python-requests.org/en/latest/user/advanced/
        print(f"ws upgrade response: {response.json()}")
        
        # Send ws requests as a message...somehow


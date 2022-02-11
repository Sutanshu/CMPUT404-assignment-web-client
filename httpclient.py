#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it
# Assignment author: Sutanshu Seth, Feb 11, 2022.
import sys
import socket
import re

# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return str(self.body)


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        headers = self.get_headers(data)
        for header in headers:
            code = re.findall(r"\D\d{3}\D", header)
            return int(code[0])
        return 500

    def get_headers(self, data):
        allHeaders = data.split("\r\n\r\n")[0]
        return allHeaders.split("\r\n")

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode("utf-8"))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def GET(self, url, args=None):

        code = 500
        body = ""

        parsedUrl = urllib.parse.urlparse(url)

        # Destructure the parsed url
        port, parsedHost, path = parsedUrl.port, parsedUrl.hostname, parsedUrl.path

        if not port:
            # Default port
            port = 80

        if not path:
            # Default path, go to root
            path = "/"

        hostName = socket.gethostbyname(parsedHost)

        self.connect(hostName, port)

        # Forming the payload that's to be sent to server
        payload = (
            "GET {} HTTP/1.1\r\nAccept: */*\r\nAccept-Encoding: */*\r\nHost: {}\r\nConnection: Close\r\n\r\n".format(
                path, parsedHost
            )
        )

        # Sending the payload
        self.sendall(payload)

        # Receiving the response, and returning status code and body
        res = self.recvall(self.socket)
        code, body = self.get_code(res), self.get_body(res)
        print(body)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        code = 500
        body = ""
        parsedUrl = urllib.parse.urlparse(url)

        # Destructure the parsed url
        port, parsedHost, path = parsedUrl.port, parsedUrl.hostname, parsedUrl.path

        if not port:
            # Default port
            port = 80

        if not path:
            # Default path, go to root
            path = "/"

        hostName = socket.gethostbyname(parsedHost)

        self.connect(hostName, port)

        if args:
            args = str(urllib.parse.urlencode(args))
        else:
            args = ""

        payload = "POST {} HTTP/1.1\r\nHost: {}\r\nAccept: /*/\r\nConnection: Close\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}\r\n\r\n".format(
            path, parsedHost, len(args), args
        )

        self.sendall(payload)
        res = self.recvall(self.socket)
        code, body = self.get_code(res), self.get_body(res)
        print(body)
        self.close()

        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))

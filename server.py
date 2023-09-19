#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2023 Dennea MacCallum
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

ROOT = 'www'

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print ("Got a request of: %s\n" % self.data)
        method = self.data.split(' ')[0]
        path = self.data.split(' ')[1]
        print(self.data)

        if method == "GET":
            self.handle_get_request(path)
        else:
            # Invalid Method
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n<html><body><h1>Method Not Allowed</h1></body></html>"
            self.request.sendall(response.encode('utf-8'))

    def handle_get_request(self, path):
        file_path = os.path.join(ROOT, path.lstrip("/"))

        if os.path.exists(file_path) and not self.bad_path(path):
            if os.path.isfile(file_path):
                # Handles files
                with open(file_path, 'r') as file:
                    content = file.read()
                    contentType = 'text/html'
                if path.split('.')[1] == 'css':
                    contentType = 'text/css'

                response = f"HTTP/1.1 200 OK\r\nContent-Type: {contentType}\r\n\r\n"
                self.request.sendall(bytearray(response + content,'utf-8'))
            else:
                # Handles directories 
                if not path.endswith('/'):
                    # Redirect to the same path with a trailing slash using HTTP 301
                    redirect_url = f"{path}/"
                    response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {redirect_url}\r\n\r\n"
                    self.request.sendall(response.encode('utf-8'))

                else:
                    index_file_path = file_path + '/index.html'
                    if os.path.isfile(index_file_path):
                        with open(index_file_path, 'r') as file:
                            content = file.read()

                        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                        self.request.sendall(bytearray(response + content,'utf-8'))

        else:
            # File was not found
            response = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
            self.request.sendall(bytearray(response,'utf-8'))

    def bad_path(self, file_path):
        directories = file_path.split("/")
        if ".." in directories:
            return True
        else:
            return False

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

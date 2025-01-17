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

# Copyright 2023 Dennea MacCallum

ROOT = 'www'

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print ("Got a request of: %s\n" % self.data)
        data_list = self.data.split()
        if len(data_list) > 1:
            method = data_list[0]
            path = data_list[1]

            if method == "GET":
                self.handle_get_request(path)
            else:
                # Invalid Method
                response = "HTTP/1.1 405 Method Not Allowed\r\n"
                self.request.sendall(response.encode('utf-8'))
        else:
            # Make sure the request has needed parameters: method and path
            response = "HTTP/1.1 400 Bad Request\r\n"
            self.request.sendall(response.encode('utf-8'))

    def handle_get_request(self, path):
        file_path = os.path.join(ROOT, path.lstrip("/"))

        if os.path.exists(file_path) and not self.is_bad_path(file_path):
            if os.path.isfile(file_path):
                # Handles files
                with open(file_path, 'r') as file:
                    content = file.read()
                    contentType = 'text/plain'
                    if path.split('.')[1] == 'css':
                        contentType = 'text/css'
                    elif path.split('.')[1] == 'html':
                        contentType = 'text/html'

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
                       self.not_found()

        else:
            self.not_found()
    
    def is_bad_path(self, path):
        # ensure that the path is within our root directory
        # reference: Chat GPT helped with lines 97 and 99
        abs_path = os.path.abspath(path)

        if abs_path.startswith(os.path.join(os.getcwd(), ROOT)):
            return False
        else:
            return True
        
    def not_found(self):
         # File was not found
        response = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>"
        self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

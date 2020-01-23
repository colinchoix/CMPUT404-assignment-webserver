#  coding: utf-8 
import socketserver
# Copyright 2020 Abram Hindle, Eddie Antonio Santos, Colin Choi
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

def parseRequest(request):
    request = request.split('\n')
    HTTPRequest = request[0]
    HTTPCommand = HTTPRequest.split()[0]
    HTTPData = HTTPRequest.split()[1]

    return (HTTPCommand, HTTPData)

def checkRedirect(requestURI):
    # TODO check if dir with os then add slash if dir and no trailing slash
    # Checks if Uri ends with a slash
    if (requestURI[-1] != "/" and "." not in requestURI.split("/")[-1]):
        #print(requestURI[-1])
        return True
    else:
        return False

def respondOK(requestURI):
    # Generate 200 response
    body = getBodyFromPath(requestURI)
    if (body == -1):
        return False

    header = "HTTP/1.1 200 OK\r\n"
    contentType = "Content-type: "+getContentType(requestURI)+";charset=utf-8\r\n"
    contentLength = "Content-Length: "+ str(len(body))+"\r\n\n"

    '''
    HTTP/1.0 200 OK
    Server: SimpleHTTP/0.6 Python/3.5.2
    Date: Tue, 21 Jan 2020 02:53:04 GMT
    Content-type: text/html
    Content-Length: 492
    Last-Modified: Fri, 10 Jan 2020 23:54:21 GMT
    '''
    response = header + contentType + contentLength + body
    return response

def movedPermanatly(requestURI):
    # Generate 301 response
    location = requestURI +"/"
    response = "HTTP/1.1 301 Moved Permanently\r\nLocation: "+location+"\r\n\n"

    return response

def pageNotFound():
    # Generate 404 response

    body = "<html><body><h1>404 PAGE NOT FOUND</h1></body></html>"

    header = "HTTP/1.1 404 File not found\r\n"
    contentType = "Content-type: text/html;charset=utf-8\r\n"
    contentLength = "Content-Length: "+ str(len(body))+"\r\n\n"

    response = header + contentType + contentLength + body
    return response

def methodNotAllowed():
    # Generate 405 response

    body = "<html><body><h1>405 METHOD NOT ALLOWED</h1></body></html>"

    header = "HTTP/1.1 405 Method Not Allowed\r\nAllow: GET, HEAD\r\n"
    contentType = "Content-type: text/html;charset=utf-8\r\n"
    contentLength = "Content-Length: "+ str(len(body))+"\r\n\n"

    response = header + contentType + contentLength + body
    return response

def createResponse(request):
    # If not a get request return a 405
    if (request[0] == 'GET'):
        # Get URI of the request
        requestURI = request[1]

        # Check if we need to redirect. Return a 301 if we do
        if(checkRedirect(requestURI)):
            return movedPermanatly(requestURI) #301
        
        # Create our 200 ok response
        OK = respondOK(requestURI)

        # Return 404 if page not found
        if (OK == False):
            return pageNotFound() #404
        else:
            return  OK

    else:
        return methodNotAllowed() # 405

def getContentType(requestURI):
    if (requestURI[-1] == "/"):
        return "text/html"
    else:
        return "text/"+requestURI.split("/")[-1].split(".")[-1]

def getBodyFromPath(requestURI):

    root = "./www"

    if (requestURI[-1] == "/"):
        root += requestURI + "index.html"
    else: 
        root += requestURI

    try:
        body = open(root).read()
        return body
    except:
        return -1

class MyWebServer(socketserver.BaseRequestHandler):
    
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        #print("Request:",parseRequest(self.data.decode()),"-"*20, sep="\n")
        
        # Parse the HTTP request
        request = parseRequest( self.data.decode() )
        # Create a HTTP response to the request
        response = createResponse(request)
        # Send the response
        #print(response)
        self.request.sendall(response.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

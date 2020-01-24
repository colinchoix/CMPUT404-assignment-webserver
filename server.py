#  coding: utf-8 
import socketserver, os
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
    """
    Parse HTTP request and return HTTP Command and the path
    """
    request = request.split('\n')
    HTTPRequest = request[0]
    HTTPCommand = HTTPRequest.split()[0]
    HTTPData = HTTPRequest.split()[1]

    return (HTTPCommand, HTTPData)

def checkRedirect(requestURI):
    """
    Checks for correct path. Directories end with a trailing /
    """
    path = "www"+requestURI+"/"

    if (requestURI[-1] != "/" and os.path.isdir(path)):
        return True
    else:
        return False

def respondOK(requestURI):
    """ 
    Generate a 200 OK response
    """
    # Get body for the response
    body = getBodyFromPath(requestURI)

    # If page is not found, return False
    if (body == -1):
        return False

    # Create the header info
    header = "HTTP/1.1 200 OK\r\n"
    contentType = "Content-type: "+getContentType(requestURI)+";charset=utf-8\r\n"
    contentLength = "Content-Length: "+ str(len(body))+"\r\n\n"
    
    # Combine headers and return the response
    response = header + contentType + contentLength + body
    return response

def movedPermanatly(requestURI):
    """ 
    Generate a 301 Moved Permanently response
    """

    # Add trailing slash to new location
    location = requestURI +"/"
    response = "HTTP/1.1 301 Moved Permanently\r\nLocation: "+location+"\r\n\n"

    return response

def pageNotFound():
    """ 
    Generate a 404 File not found response
    """

    # Create a simple 404 body to display if somebody gets this error
    body = "<html><body><h1>404 PAGE NOT FOUND</h1></body></html>"

    # Create the header info
    header = "HTTP/1.1 404 File not found\r\n"
    contentType = "Content-type: text/html;charset=utf-8\r\n"
    contentLength = "Content-Length: "+ str(len(body))+"\r\n\n"

    # Combine headers and return the response
    response = header + contentType + contentLength + body
    return response

def methodNotAllowed():
    """ 
    Generate a 405 Method Not Allowed
    """

    body = "<html><body><h1>405 METHOD NOT ALLOWED</h1></body></html>"

    # Create the header info
    header = "HTTP/1.1 405 Method Not Allowed\r\nAllow: GET, HEAD\r\n"
    contentType = "Content-type: text/html;charset=utf-8\r\n"
    contentLength = "Content-Length: "+ str(len(body))+"\r\n\n"

    # Combine headers and return the response
    response = header + contentType + contentLength + body
    return response

def createResponse(request):
    """
    Decides which repsonse the server should reply with
    """

    
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
        # If not a GET request return a 405
        return methodNotAllowed() # 405

def getContentType(requestURI):
    """
    Parse out and return what type of file the client is requesting
    """

    if (requestURI[-1] == "/"):
        return "text/html"
    else:
        return "text/"+requestURI.split("/")[-1].split(".")[-1]

def getBodyFromPath(requestURI):
    """
    Given a path, return the requested content
    """

    # Files requested will be served from ./www
    root = "./www"

    # Server index.html to paths that ends with /
    if (requestURI[-1] == "/"):
        root += requestURI + "index.html"
    else: 
        root += requestURI

    # Prevent path from accessing file in the parent directories of ./www
    directories = requestURI.split("/")

    level = 0 # keep track of how many directories deep we are
    for dir in directories:

        if dir != "..":
            level += 1
        elif dir == "..":
            level -= 1
        
        # Return a 404 if we try to go out of root directory
        if level < 0:
            return -1


    # Try to open the requested resource
    try:
        body = open(root).read()
        return body
    # 404 if file not found
    except:
        return -1



class MyWebServer(socketserver.BaseRequestHandler):
    
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        
        # Parse the HTTP request
        request = parseRequest( self.data.decode() )
        
        # Create a HTTP response to the request
        response = createResponse(request)
        
        # Send the response
        self.request.sendall(response.encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

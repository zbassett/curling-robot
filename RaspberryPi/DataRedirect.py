import SocketServer
import requests

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

	#determine the type of request and make an HTTP post to Django server with payload
	if self.data[:4] == 'uid:':         #RFIDreading
		payload = {'payloadvalue': ''}
		payload['payloadvalue'] = self.data
		r = requests.post('http://localhost:8088/curling/rfid/', payload)
	if self.data[:6] == 'shot1:':         #near distance reading
		payload = {'payloadvalue': ''}
		payload['payloadvalue'] = self.data
		r = requests.post('http://localhost:8088/curling/shot1/', payload)
	if self.data[:6] == 'shot2:':         #second distance reading
		payload = {'payloadvalue': ''}
		payload['payloadvalue'] = self.data
		r = requests.post('http://localhost:8088/curling/shot2/', payload)
	if self.data[:6] == 'shot3:':         #far tee reading
		payload = {'payloadvalue': ''}
		payload['payloadvalue'] = self.data
		r = requests.post('http://localhost:8088/curling/shot3/', payload)

if __name__ == "__main__":
    HOST, PORT = "localhost", 10000

    # Create the server, binding to localhost on port 10000
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
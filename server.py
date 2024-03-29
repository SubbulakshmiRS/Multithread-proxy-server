import socket
import sys
import threading
#import signal
	

def proxy_thread(clientSocket, client_address, config):
	# get the request from browser
	reqbinary = clientSocket.recv(config['MAX_REQUEST_LEN'])
	request = reqbinary.decode('utf-8')

	# parse the first line
	first_line = request.split('\n')[0]

	# get url
	url = first_line.split(' ')[1]

	reqtype = first_line.split(' ')[0]

	if (reqtype == 'GET' or reqtype == 'POST'):

		http_pos = url.find("://") # find pos of ://
		if (http_pos==-1):
			temp = url
		else:
			temp = url[(http_pos+3):] # get the rest of url

		port_pos = temp.find(":") # find the port pos (if any)

		# find end of web server
		webserver_pos = temp.find("/")
		if webserver_pos == -1:
			webserver_pos = len(temp)

		webserver = ""
		port = -1
		if (port_pos==-1 or webserver_pos < port_pos): 

			# default port 
			port = 80 
			webserver = temp[:webserver_pos] 

		else: # specific port 
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		#s.settimeout(config['CONNECTION_TIMEOUT'])
		s.connect((webserver, port))
		s.send(reqbinary)	#sendall should be tried too

		while 1:
			# receive data from web server
			data = s.recv(config['MAX_REQUEST_LEN'])

			if (len(data) > 0):
				clientSocket.send(data) # send to browser/client
			else:
				break

	else:
		data = '<html><head><title>Error</title></head><body><p>The proxy server does not handle requests other than GET and POST requests</p></body></html>'
		data = data.encode('utf-8')
		clientSocket.send(data)

def start_server(config):

	#signal.signal(signal.SIGINT, shutdown);
	__clients = {}

	# Create a TCP socket
	try:
		server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	except:
		print("Socket failed to be created. Error: " + str(sys.exc_info()))
		sys.exit()

	# Set socket options to re-use addresses and ports to remove correspinding errors
	try:
		#server_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR | socket.SO_REUSEPORT, 1)
		server_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	except:
		print("Error in setting socket options. Error: " + str(sys.exc_info()))
		sys.exit()

	# Bind the socket to a host, and a port   
	try:
		server_fd.bind((config['HOST_NAME'], config['BIND_PORT']))

	except:
		print("Bind failed. Error: " + str(sys.exc_info()))
		sys.exit()

	# Listen for incoming connections, max queue size is currently 10
	try:
		server_fd.listen(10)
	except:
		print("Error in listening to socket. Error: " + str(sys.exc_info()))
		sys.exit()

	while True:

		# Establish the connection
		try:
			(clientSocket, client_address) = server_fd.accept()
		except:
			print("Error in accepting incoming connection. Error: " + str(sys.exc_info()))
			sys.exit();

	
		try:
			#self._getClientName(client_address)
			d = threading.Thread(group = None, target = proxy_thread, name = None, args=(clientSocket, client_address, config), kwargs = {}, daemon = None)
			d.setDaemon(True)
			d.start()
		except:
			print("Error in creating thread for request. Error: " + str(sys.exc_info()))
			sys.exit();


config = {
	'HOST_NAME': "127.0.0.1",
	'BIND_PORT': 12345,
	'MAX_REQUEST_LEN': 4096,
	'CONNECTION_TIMEOUT': 7,
}

start_server(config)
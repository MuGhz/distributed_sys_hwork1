#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import sys
import os
import time
import random

def generate_header(msg,code,content_type):
	header = ""
	if(code == 200):
		header = 'HTTP/1.1 200 OK\n'
	elif(code == 302):
		header = 'HTTP/1.1 302 Found\n'
		header += 'Location: /hello-world\n'
	elif(code == 404):
		header =  'HTTP/1.1 404 Not Found\n'
	elif(code == 400):
		header = 'HTTP/1.1 400 Bad request\n'
	elif(code == 501):
		header = 'HTTP/1.1 501 Not implemented\n'
	header += 'Content-Type: '+content_type+'\n'
	header += 'Content-Length: '+str(len(msg))+'\n'
	header += 'Connection: close\n\n'
	return header

def html_wraper(str):
	return '<html><head></head><body><p>'+str+'</p></body></html>'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
host = "localhost" # Get local machine name
port = int(sys.argv[1])                # Reserve a port for your service.
print ("Host :", host ," Port :", port)
s.bind((host, port))        # Bind to the port
s.listen(10)                 # Now wait for client connection.
while True:
	conn, addr = s.accept()     # Establish connection with client.
	print ('Got connection from', addr)
	data = conn.recv(1024) #receive data from client
	data = bytes.decode(data) #decode it to string
	try :
		data_line = data.split('\n')
		content_type = ''
		content_length = ''
		name = ''
		for line in data_line :
			if line.startswith('Content-Type') :
				content_type = line.split(' ')[1]
				content_type = content_type.replace(' ','')
			elif line.startswith('Content-Length'):
				content_length = line.split(' ')[1]
				content_length = content_length.replace(' ','')
			elif line.startswith('name=') :
				name = line.split('=')[1]
				name=name.replace('+',' ')
				name=name.encode('utf-8')
		request_method = data_line[0].split(' ')[0] #determine request method  (HEAD and GET are supported)
		request_url = data_line[0].split(' ')[1]
		request_format = data_line[0].split(' ')[2]
		print ("Method: ", request_method)
		print ("Path: ",request_url)
		print ("Request body: ", data)
	except :
		print ('error in data parsing')
		print (data)

	if not request_format.startswith("HTTP/1.0") and not request_format.startswith("HTTP/1.1") :
		print ("Bad request")
		msg=html_wraper("400 Bad request")
		msg=msg.encode('utf-8')
		header = generate_header(msg,400,'text/html')
		try :
			conn.send(header.encode('utf-8'))
			conn.send(msg)
			conn.close()
		except :
			print ('error connection while sending response')

	elif request_method != 'GET' and request_method != 'POST' :
		print ('request method not implemented')
		msg=html_wraper('501 Not implemented')
		msg=msg.encode('utf-8')
		header = generate_header(msg,501,'text/html')
		try :
			conn.send(header.encode('utf-8'))
			conn.send(msg)
			conn.close()
		except :
			print ('error connection while sending response')

	elif request_url == '/' :
		header = generate_header('',302,'text/html')
		try :
			conn.send(header.encode('utf-8'))
			conn.close()
		except :
			print ('error connection while sending response')

	elif request_url == '/hello-world' :
		page = ''
		try :
			file = open(os.getcwd()+"/hello-world.html","rb")
			page = file.read()
			file.close()
		except :
			print ("File not found")
		code = 200
		if request_method == 'GET' :
			page = page.replace(b'__HELLO__',b'World')
		elif request_method == 'POST' :
			if not 'application/x-www-form-urlencoded' in content_type:
				msg = '400 Bad Request'
				page=msg.encode('utf-8')
				code=400
			else:
				page = page.replace(b'__HELLO__',name)
		header = generate_header(page,code,'text/html')
		try :
			print('page :',page)
			conn.send(header.encode('utf-8'))
			conn.send(page)
			conn.close()
		except :
			print ('error connection while sending response')

	elif request_method == 'GET' and request_url == '/style':
		style = ''
		try :
			file = open(os.getcwd()+"/style.css","rb")
			style = file.read()
			file.close()
		except :
			print ('Image not found')
		header = generate_header(style,200,'text/css')
		try :
			conn.send(header.encode('utf-8'))
			conn.send(style)
			conn.close()
		except:
			print ('error connection while sending response')

	elif request_method == 'GET' and request_url == '/background':
		image = ''
		try :
			file = open(os.getcwd()+"/background.jpg","rb")
			image = file.read()
			file.close()
		except :
			print ('Image not found')
		header = generate_header(image,200,'image/jpg')
		try :
			conn.send(header.encode('utf-8'))
			conn.send(image)
			conn.close()
		except :
			print ('error connection while sending response')

	elif request_method == 'GET' and request_url.startswith('/info'):
		type = request_url.split('?')[1].split('=')[1]
		response = ''
		if type == 'time' :
			response = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		elif type == 'random' :
			response = str(random.randint(0,100000))
		else :
			response = 'No Data'
		response = response.encode('utf-8')
		header = generate_header(response,200,'text/plain')
		try :
			conn.send(header.encode('utf-8'))
			conn.send(response)
			conn.close()
		except:
			print ('error connection while sending response')

	else :
		print ('404 Not Found')
		msg=html_wraper('404 Not Found')
		msg=msg.encode('utf-8')
		header = generate_header(msg,404,'text/html')
		try :
			conn.send(header.encode('utf-8'))
			conn.send(msg)
			conn.close()
		except :
			print ('error connection while sending response')

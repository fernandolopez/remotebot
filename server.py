#!/usr/bin/python

#from http.server import HTTPServer, BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
import json


from robot import *
b = Board()
r = Robot(b, 21)



class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if (self.command != 'GET'): return
		print(self.rfile.read())
		print(self.path)
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(b"<html><body>ok get</body></html>\n\n")
	
	def do_POST(self):
		if (self.command != 'POST'): return
		#if (not self.rfile)): print(self.rfile.read())
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
			})
		print('\n'.join(form.getlist('comandos')))
		comando = json.loads(b'\n'.join(form.getlist('comandos')))
		func = getattr(r, comando['opcode'])
		p1 = comando['p1']
		p2 = comando['p2']
		func(p1, p2)

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(b"<html><body>ok post</body></html>\n\n")



address = ('', 8000)
httpd = HTTPServer(address, RequestHandler)
httpd.serve_forever()

b.exit()

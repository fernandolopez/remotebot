#!/usr/bin/python

#from http.server import HTTPServer, BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
import json
import dispatcher

class RequestHandler(BaseHTTPRequestHandler):
	defaultPage = "/clients/raw/javascript.html"
	def do_GET(self):
		if (self.command != 'GET'): return
		#print(self.rfile.read())
		print(self.path)
		if self.path != self.defaultPage:
			self.send_response(302)
			self.send_header("Location", self.defaultPage)
			self.end_headers()
			return
			
		try:
			f = open(self.defaultPage.lstrip('/'), 'r')
			body = f.read()
            f.close()
			self.send_response(200)
		except IOError:
			body = """<html><head><title>Error</title></head>
			<body>Error al leer el archivo {0}</body></html>
			""".format(self.defaultPage)
			self.send_response(503)

		self.send_header("Content-type", "text/html")
		self.end_headers()			
		self.wfile.write(str(body))
	
	def do_POST(self):
		if (self.command != 'POST'): return
		#if (not self.rfile)): print(self.rfile.read())
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
			})
		result = dispatcher.execute(form)
        

		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(str(result))



address = ('', 8000)
httpd = HTTPServer(address, RequestHandler)
httpd.serve_forever()

#!/usr/bin/python

#from http.server import HTTPServer, BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
import json
import dispatcher
import select
from errors import ServerException

class RequestHandler(BaseHTTPRequestHandler):
	defaultPage = "/clients/raw/javascript.html"
	localAPK = "/clients/android/remotebot.apk"
	def do_GET(self):
		if (self.command != 'GET'):
			return
		#print(self.rfile.read())
		print(self.path)
		
		if self.path == self.defaultPage:
			mimetype = "text/html"
		elif self.path == self.localAPK:
			mimetype = "application/vnd.android.package-archive"
		else:
			self.send_response(302)
			self.send_header("Location", self.defaultPage)
			self.end_headers()
			return
			
		try:
			f = open(self.path.lstrip('/'), 'r')
			body = f.read()
			f.close()
			self.send_response(200)
		except IOError:
			body = """<html><head><title>Error</title></head>
			<body>Error al leer el archivo {0}</body></html>
			""".format(self.path)
			mimetype = "text/html"
			self.send_response(500)
		
		self.send_header("Content-type", mimetype)
		self.end_headers()			
		self.wfile.write(str(body))
	
	def do_POST(self):
		import StringIO
		if (self.command != 'POST'):
			return
		#data = StringIO.StringIO(self.rfile.read(int(self.headers['Content-Length'])))
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
			})
		#data.close()
		try:
			result = dispatcher.execute(form)
		except ServerException as e:
			print(e)
			result = e.dumpJSON()
		

		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(str(result))



address = ('', 8000)
httpd = HTTPServer(address, RequestHandler)
try:
	httpd.serve_forever()
except (Exception, KeyboardInterrupt) as e:
	print(e)
	dispatcher.free()

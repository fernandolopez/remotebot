#!/usr/bin/python
#~ remotebot, Python web server for remote interaction with duinobot API.
#~ Copyright (C) 2012  Fernando E. M. López <flopez AT linti.unlp.edu.ar>
#~ 
#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.
#~ 
#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.
#~ 
#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
	# Disable logging DNS lookups
	def address_string(self):
		return str(self.client_address[0])
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
			self.send_header("Content-Length", len(body))
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
		if (self.command != 'POST'):
			return
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
			})
		try:
			result = dispatcher.execute(form)
		except ServerException as e:
			print(e)
			result = e.dumpJSON()
		
		result = str(result)
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.send_header("Content-Length", len(result))
		self.end_headers()
		self.wfile.write(result)
		self.wfile.write("\n")
		print("**************************************")
		print(result)
		print("**************************************")


import socket
address = ('', 8000)
httpd = HTTPServer(address, RequestHandler)
#httpd.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)
try:
	httpd.serve_forever()
except (Exception, KeyboardInterrupt) as e:
	print(e)
	dispatcher.free()

import json
import traceback

class ServerException(Exception):
	def __init__(self, originalException):
		Exception.__init__(self, originalException)
		self.originalName = repr(originalException)
		self.stackTrace = traceback.format_exc()
	
	def dumpJSON(self):
		return json.dumps({
				'type': 'exception',
				'name': self.originalName,
				'stacktrace': self.stackTrace
			})


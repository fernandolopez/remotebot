import sys

if sys.version_info.major >= 3:
    class RequestHandlerMixin(object):
        def write(self, data):
            self.wfile.write(bytes(data, 'utf-8'))
else:
    class RequestHandlerMixin(object):
        def write(self, data):
            self.wfile.write(data)

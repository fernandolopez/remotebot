# -*- encoding: utf-8 -*-

def boards():
	return ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']

class Board:
	def __init__(self, device="/dev/ttyUSB0"):
		self.device = device
		print "Se instancia " + device

	def __str__(self):
		return "Board(" + self.device + ")"
	def exit(self):
		pass
	def report(self):
		return (1, 2, 3, 4, 5, 6)

class Robot:
	def __init__(self, board, id):
		self.board = board
		self.id = id
		print "Se instancia el robot " + str(id) + "en la placa" + str(board)
	
	def __parametros(self, *args):
		print "Con los parámetros " + str(args)

	def __getattr__(self, name):
		print "Se invoca en: " + str((self.board.device, self.id)) + " el método: " + name
		return self.__parametros

	def getWheels(self):
		return (13, 24)

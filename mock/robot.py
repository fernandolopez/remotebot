# -*- encoding: utf-8 -*-
import time
def boards():
	return ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']

class Board:
	def __init__(self, device="/dev/ttyUSB0"):
		self.device = device
		print("Se instancia " + device)
		time.sleep(2)
	def __str__(self):
		return "Board(" + self.device + ")"
	def exit(self):
		pass
	def report(self):
		time.sleep(5)
		return [1, 2, 3, 4, 5, 6]

class Robot:
	def __init__(self, board, id):
		self.board = board
		self.id = id
		print("Se instancia el robot " + str(id) + "en la placa" + str(board))
	
	def __parametros(self, *args):
		print("Con los parámetros " + str(args))
		time.sleep(1)

	def __getattr__(self, name):
		print("Se invoca en: " + str((self.board.device, self.id)) + " el método: " + name)
		return self.__parametros

	def getWheels(self):
		return (13, 24)
	def ping(self):
		return 100
	def getLine(self):
		return (44, 25)
	def getObstacle(self, distance=20):
		return self.ping() < distance

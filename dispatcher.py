from duinobot import *
#from mock.robot import *
import json
from errors import ServerException
from serial.serialutil import SerialException

__robot = {}
__board = {}


def robot_execute(message):
    boardid = message['board']['device']
    robotid = (boardid, message['id'])
    if message['command'] == '__init__':
        if boardid in __board and not robotid in __robot:
            __robot[robotid] = Robot(__board[boardid], message['id'])
    else:
        return getattr(__robot[robotid], message['command'])(*message['args'])
    return None
    
def board_execute(message):
    device = message['board']['device']
    print "A ver si conecta... " + device
    if message['command'] == '__init__' and not device in __board:
        __board[device] = Board(device)
    return None
    
def module_execute(message):
    if message['command'] == 'boards':
            return boards()
    return None


__handler = {
    'robot': robot_execute,
    'board': board_execute,
    'module': module_execute
}

def execute(form):
    returnList = []
    print form
    try:
        command = '\n'.join(form.getlist("commands"))
        cmdList = json.loads(command)
        for cmdObject in cmdList:
            if not 'args' in cmdObject:
                cmdObject['args'] = ()
            returnList.append(__handler[cmdObject["target"]](cmdObject))
    except (TypeError, ValueError, KeyError, SerialException) as e:
        raise ServerException(e)
    
    return json.dumps({
        'type': 'returnvalues',
        'values': returnList
        })

def free():
    for each in __board.values():
        each.exit()

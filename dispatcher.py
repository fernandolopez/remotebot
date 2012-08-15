from robot import *
import json
import cgi
import traceback

__robot = {}
__board = {}


def robot_execute(message):
    boardid = message['board']['device']
    robotid = (boardid, message['id'])
    if message['command'] == '__init__':
        if boardid in __board and not robotid in __robot:
            __robot[robotid] = Robot(__board[boardid], message['id'])
    else:
        getattr(__robot[robotid], message['command'])(*message['args'])
    return "Ok"
    
def board_execute(message):
    device = message['board']['device']
    if message['command'] == '__init__' and not device in __board:
        __board[device] = Board(device)
    return "board"
    
def module_execute(message):
    #print message
    return "module"


__handler = {
    'robot': robot_execute,
    'board': board_execute,
    'module': module_execute
}

def execute(form):
    response = ""
    print form
    try:
        command = '\n'.join(form.getlist("commands"))
        cmdList = json.loads(command)
        for cmdObject in cmdList:
            response += __handler[cmdObject["target"]](cmdObject)
    except TypeError as e:
        return "Server error: " + traceback.format_exc()
    except ValueError as e:
        return "Server error: " + traceback.format_exc()
    except KeyError as e:
        return "Server error: " + traceback.format_exc()
    
    return response
    

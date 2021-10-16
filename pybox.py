#!/usr/bin/env python3
#  coding: utf-8


"""
    PyBox steering module

    File name: pybox.py
    Author: Patrick Bard
    Date created: 2018-05-24
    Date last modified: 2018-05-24
    Python Version: 2.7.14 or greater and 3.6.5 or greater
"""


__author__     = "Patrick Bard"
__copyright__  = "Copyright 2018, Laboratoire d'Etude de l'Apprentissage et du Developpement (LEAD)"
__credits__    = ["Patrick Bard"]
__license__    = "GPL"
__version__    = "1.0.0"
__maintainer__ = "Patrick Bard"
__email__      = "Patrick Bard@u-bourgogne.fr"
__status__     = "Production"


import serial
import serial.tools.list_ports
import time


DELAY = 0.010 # s

TIMESTAMP = 2
STATE     = 1
KEY       = 0

ON  = '1'
OFF = '0'

GREEN  = '4'
RED    = '3'
BLUE   = '2'
YELLOW = '1'
ALL    = '0'

BAUDRATE    = 9600 # bauds
DESCRIPTION = "Arduino Leonardo"

FIRST =  0
LAST  = -1


class PyBoxNoConnectionError(Exception) :

    """PyBox not connected"""

    def __init__(self, message) :
        self.message = message

		
class PyBoxMultipleConnectionsError(Exception) :

    """Multiples PyBoxes connected"""

    def __init__(self, message) :
        self.message = message

		
class PyBoxBusyError(Exception):

    """PyBox busy"""

    def __init__(self, message) :
        self.message = message


class PyBoxDisconnectedError(Exception) :

    """ERROR : PyBox disconnected"""

    def __init__(self, message) :
        self.message = message


def open() :

    """PyBox initialization"""
	
    device = list()
    for object in serial.tools.list_ports.comports() :
        if DESCRIPTION in object.description :
            device.append(object.device)
            break

    if len(device) == 0 :
        raise PyBoxNoConnectionError("ERROR : No PyBox connected")

    if len(device) > 1 :
        raise PyBoxMultipleConnectionsError("ERROR : Multiple PyBoxes connected")

    try :
        handle = serial.Serial(device[FIRST], BAUDRATE)
        handle.open()
    except serial.SerialException :
        pass
    try :
        handle
    except UnboundLocalError :
        raise PyBoxBusyError("ERROR : PyBox busy")

    time.sleep(DELAY)

    off(handle)

    time.sleep(DELAY)

    clean(handle)

    return(handle)


def close(handle) :

    """PyBox release"""
	
    handle.close()


def write(handle, data) :

    """PyBox low level write"""

    try :
        handle.write(bytearray(data.encode('utf-8')))
        handle.flush()
    except serial.serialutil.SerialException :
        raise PyBoxDisconnectedError("ERROR : PyBox disconnected")


def read(handle) :

    """PyBox low level read"""
	
    data = bytearray()
    while True :
        try:
            size = handle.in_waiting
        except serial.serialutil.SerialException:
            raise PyBoxDisconnectedError("ERROR : PyBox disconnected")
        if size == 0 :
            break
        else :
            try :
                data = handle.read(size)
            except serial.serialutil.SerialException :
                raise PyBoxDisconnectedError("ERROR : PyBox disconnected")
    data = str.split(data.decode('utf-8'))
    if len(data) != 0 :
        return(data[LAST][KEY], data[LAST][STATE], ''.join([data[LAST][index] for index in range(TIMESTAMP, len(data[LAST]))]))
    else :
        return(None)


def clean(handle) :

    """PyBox data purge"""
	
    while True :
        if read(handle) is None :
            break

			
def on(handle, index) :

    """PyBox given LED switch on"""
	
    write(handle, index)


def off(handle) :

    """PyBox all LED switch off"""
	
    write(handle, ALL)


if __name__ == "__main__" :


    TRIALS = 20

    SUCCESS = 0
    FAILURE = -1


    key = {YELLOW: "YELLOW", BLUE: "BLUE  ", RED: "RED   ", GREEN: "GREEN "}
    state = {OFF: "OFF", ON: "ON "}


    print("Initializing box")

    try :
        handle = open()
    except (PyBoxNoConnectionError, PyBoxMultipleConnectionsError, PyBoxBusyError) as error:
        print(error.message)
        exit(FAILURE)

    time.sleep(DELAY)


    print("Switching key YELLOW ON")
    try :
        on(handle, YELLOW)
    except PyBoxDisconnectedError as error :
        print(error.message)
        exit(FAILURE)
    time.sleep(1)

    print("Switching key BLUE   ON")
    try:
        on(handle, BLUE)
    except PyBoxDisconnectedError as error:
        print(error.message)
        exit(FAILURE)
    time.sleep(1)

    print("Switching key RED    ON")
    try:
        on(handle, RED)
    except PyBoxDisconnectedError as error:
        print(error.message)
        exit(FAILURE)
    time.sleep(1)

    print("Switching key GREEN  ON")
    try:
        on(handle, GREEN)
    except PyBoxDisconnectedError as error:
        print(error.message)
        exit(FAILURE)
    time.sleep(1)

    print("Switching ALL keys   OFF")
    try:
        off(handle)
    except PyBoxDisconnectedError as error:
        print(error.message)
        exit(FAILURE)
    time.sleep(1)


    print("Cleaning box event queue")
    try :
        clean(handle)
    except PyBoxDisconnectedError as error:
        print(error.message)
        exit(FAILURE)
    time.sleep(DELAY)


    trial = 0
    print("Waiting a key is pressed ({0} trials) :".format(TRIALS))
    while trial < TRIALS:
        try :
            data = read(handle)
        except PyBoxDisconnectedError as error:
            print(error.message)
            exit(FAILURE)
        if data is not None:
            print("$ Key", key[data[KEY]], state[data[STATE]], "@", data[TIMESTAMP], "ms")
            trial += 1


    print("Exiting")

    handle.close()

    exit(SUCCESS)
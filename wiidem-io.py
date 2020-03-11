#!/usr/bin/python3
# -*- coding: utf-8 -*-
# wiidem_el02.py

##########################
######## LIBRARIES #######
##########################
import settings
from dal import DataAccessLayer
from datetime import datetime
import time
import os
import threading
import RPi.GPIO as GPIO


#################################
######## GLOBAL VARIABLES #######
#################################
part_counter = {}

########################
######## LOGGING #######
########################
def getDateTime():
    now = datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S.%f", now)

def saveGpioLog(msg, level="INFO"):
    filename = settings.LOG_FILE_IO
    saveLog(filename, msg, level)
    print(msg)

def saveLog(filename, msg, level):
    pid = str(os.getpid())
    f = open(filename, "a+")
    f.write(getDateTime() + ', ' + pid + ', ' + level + ', ' + msg + "\n")
    f.close()

def logError(errorId, e):
    saveGpioLog(settings.MESSAGES.ERROR[errorId], 'ERROR')

def logInfo(message):
    saveGpioLog(message)

########################################
######## HARDWARE SETUP FUNCTION #######
########################################

def gpioSetup():
    """ Se configuran los puertos de INPUT """
    # Setup the wiring
    GPIO.setmode(GPIO.BOARD)
    # Setup Ports
    GPIO.setup(settings.LED_PORT, GPIO.OUT)
    for input in settings.INPUTS:
        channel = settings.INPUTS[input]['CHANNEL']
        default_state = settings.INPUTS[input]['DEFAULT_STATE']
        GPIO.setup(channel, GPIO.IN, pull_up_down = default_state)
    # configure event callbacks
    for input in settings.INPUTS:
        channel = settings.INPUTS[input]['CHANNEL']
        event = settings.INPUTS[input]['EVENT']
        GPIO.add_event_detect(channel, event, callback = genericSensorEvent, bouncetime = settings.SWITCH_DEBOUNCE_TIME)
    # output sensors current values
    for input in settings.INPUTS:
        channel = settings.INPUTS[input]['CHANNEL']
        if GPIO.input(channel):
            logInfo(str(channel) + ' Input is HIGH')
        else:
            logInfo(str(channel) + ' Input is LOW')
    # init counter vars
    for input in settings.INPUTS:
        part_counter[input] = 0

def genericSensorEvent(channelId):
    global part_counter
    blink()
    for input in settings.INPUTS:
        if settings.INPUTS[input]['CHANNEL'] == channelId:
            logInfo('Event detected on channel ' + str(channelId) + ' / ' + input)
            part_counter[input] += 1
            if part_counter[input] >= settings.INPUTS[input]['PART_COUNTER']:
                saveSensorData(input, 1)
                part_counter[input] = 0 # counter is cleaned

# clean up GPIO before exit
def resetGpio():
    logInfo(settings.MESSAGES['RESET'])
    GPIO.cleanup()


###################################
######### OTHER FUNCTIONS #########
###################################
def blink(times = 1):
    for i in range(0, times):
        GPIO.output(settings.LED_PORT, GPIO.HIGH)  # Green LED ON
        time.sleep(0.1)
        GPIO.output(settings.LED_PORT, GPIO.LOW)  # Green LED OFF

def saveSensorData(sensor, production):
    """ Guarda la produccion en la base de datos interna """
    try:
        db = DataAccessLayer()
        connection = db.getOnlyConnection()
        db.saveSensorData(connection, sensor, production)
        counter = db.countSynchedRecords(connection)
        reset = False
        if counter >= settings.RESTART_PART_COUNTER:
            reset = True
            db.deleteSynchedRecords(connection)
        connection.close()
        if reset:
            resetGpio()
            logInfo('Restarting service counted ' + str(counter) + ' records')
            os.system('sudo restart-wiidem-io')
            exit()
    except Exception as e:
        logError('db-error', e)

#######################
######## MAIN #########
#######################
try:
    if __name__ == '__main__':
        os.system('clear')  # clear screen
        START_MESSAGE = "Starting IO service for Wiidem Sensor Gadget #" + str(settings.GADGET_CODE)
        logInfo(START_MESSAGE)
        db = DataAccessLayer()
        db.initDb()
        gpioSetup()

        while True:
            time.sleep(settings.SLEEP_TIME_IO)

except (KeyboardInterrupt, SystemExit, Exception):
    resetGpio()
finally:
    resetGpio()
    logInfo(settings.MESSAGES['EXIT'])

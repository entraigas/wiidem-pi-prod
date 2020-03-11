#!/usr/bin/python3
# -*- coding: utf-8 -*-
# wiidem_el02.py

##########################
######## LIBRARIES #######
##########################
import settings
from dal import DataAccessLayer
import requests
from datetime import datetime
import time
import os
from requests.exceptions import RequestException
import RPi.GPIO as GPIO
import socket
import json


########################
######## LOGGING #######
########################
def getDateTime():
    now = datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S.%f", now)

def saveApiLog(msg, level="INFO"):
    try:
        filename = settings.LOG_FILE_API
        saveLog(filename, msg, level)
        print(msg)
    except Exception as e:
        print(e)

def saveLog(filename, msg, level):
    pid = str(os.getpid())
    f = open(filename, "a+")
    f.write(getDateTime() + ', ' + pid + ', ' + level + ', ' + msg + "\n")
    f.close()

def logError(errorId, e):
    saveApiLog(settings.MESSAGES.ERROR[errorId], 'ERROR')

def logInfo(message):
    saveApiLog(message)

###################################
######### OTHER FUNCTIONS #########
###################################
def blink(times = 1):
    for i in range(0, times):
        GPIO.output(settings.LED_PORT, GPIO.HIGH)  # Green LED ON
        time.sleep(0.1)
        GPIO.output(settings.LED_PORT, GPIO.LOW)  # Green LED OFF

def checkNetworkConnection(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False

def checkWiidemServerConnection():
    return checkNetworkConnection(settings.SERVER_IP, settings.SERVER_PORT, settings.SERVER_TIMEOUT)

def syncRecords():
    """
    Envio producción de pieza a la API
    """
    counter = 0
    db = DataAccessLayer()
    rows = db.getPendingRecords()
    for row in rows:
        rowid = row[0]
        sensor = row[1]
        qty = row[2]
        sync_ok = sendApiRequest(sensor, qty)
        if sync_ok:
            db.markRecordAsSynched(rowid)
            counter = counter + 1
        else:
            logError('api-error')
    return counter

def sendApiRequest(sensor, production):
    """
    sensor: str
       Sensor's name that sensed the part production.
    production: int
       Part production to send to API.
    """
    url = settings.WIIDEM_DEMO_API
    payload = {
        "GadgetId": settings.GADGET_CODE,
        "Counter": "G",
        "Operation": "S",
    }
    headers = {
        'Content-Type': 'application/json',
         '__RequestVerificationSource': 'SrcRefM',
         '__RequestVerificationToken': 'YNBNYUKJGHJ122:TDBHYTRNTBVW684vt'
    }
    try:
        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        logInfo('update ' + sensor + ' qty ' + str(production))
        return True
    except RequestException as e:
        logInfo('could not update ' + sensor + ' qty ' + str(production))
        return False


#######################
######## MAIN #########
#######################
try:
    if __name__ == '__main__':
        os.system('clear')  # clear screen
        START_MESSAGE = "Starting API service for Wiidem Sensor Gadget #" + str(settings.GADGET_CODE)
        logInfo(START_MESSAGE)
        db = DataAccessLayer()
        db.initDb()

        # flags
        is_first_time = True
        is_client_online = False
        is_server_online = False
        has_unsync_data = False


        while True:
            # Online Wiidem Server Check
            is_server_online = checkWiidemServerConnection()
            if is_server_online:
                if is_first_time:
                    is_first_time = False
                    msg_success = settings.MESSAGES['SERVER_ONLINE']
                    logInfo(msg_success)

                counter = syncRecords()
                if counter > 0:
                    logInfo( str(counter) + ' records synched')

            else: # offline wiidem_server
                logError('server-offline')

            time.sleep(settings.SLEEP_TIME_API)

except KeyboardInterrupt as e:
    logInfo(settings.MESSAGES['KEYBOARD_INTERRUPTION'])
finally:
    # clean up GPIO on normal exit
    print(settings.MESSAGES['EXIT'])

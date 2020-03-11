#!/usr/bin/python3
# -*- coding: utf-8 -*-
# settings.py
# Wiidem Demo Setting File

import RPi.GPIO as GPIO

############################
####### Gadget Setup #######
############################

# Machine Number
GADGET_CODE = 1038 # Gadget ID
SLEEP_TIME_IO = 1.0 # in seconds
SLEEP_TIME_API = 1.0 # in seconds
MESSAGES = {
    'ERROR': {
        'gadget-offline': 'No network access. Gadget is offline',
        'server-offline': 'Server is offline. Could not connect to Wiidem DB Server',
        'db-error': 'Could not connect to sqlite3 DB',
        'api-error': 'Could not connect to API Server'
    },
    'SERVER_ONLINE': 'Network is working! Wiidem DB Server is online',
    'KEYBOARD_INTERRUPTION': 'Program ended by keyboard interruption',
    'RESET': 'Clean up GPIO ports',
    'EXIT': 'Program ended by keyboard interruption'
}


####################################################
######## Hardware Setup (EL-02 Sensors GPIO) #######
####################################################
"""
# SENSORs for EL-02a model (Fama?)
SENSOR1 = 35; SENSOR2 = 29; SENSOR3 = 31; SENSOR4 = 33

# SENSORs for EL-02b model
SENSOR1 = 29; SENSOR2 = 31; SENSOR3 = 33; SENSOR4 = 37
"""
#CHANNEL1, CHANNEL2, CHANNEL3, CHANNEL4 = 35, 29, 31, 33 # EL-02a model
CHANNEL1, CHANNEL2, CHANNEL3, CHANNEL4 = 29, 31, 33, 37 # EL-02b model

"""
DEFAULT_STATE = [GPIO.PUD_UP, GPIO.PUD_DOWN]
Is the default state of the input/button.
GPIO.PUD_UP means "pulled-up", and therefore when the button is not pressed, the pin is high. When the button is pressed, the pin goes low

EVENT = [GPIO.RISING, GPIO.FALLING, GPIO.BOTH]
Is the event we try to catch: when the button is falling or rising (or both of them)
"""
INPUTS = {
    'MQ01': {
        'CHANNEL': CHANNEL1,
        'DEFAULT_STATE': GPIO.PUD_UP,
        'EVENT': GPIO.FALLING,
        'PART_COUNTER': 1,
    },
    # 'MQ02': {
    #     'CHANNEL': CHANNEL2,
    #     'DEFAULT_STATE': GPIO.PUD_DOWN,
    #     'EVENT': GPIO.RISING,
    #     'PART_COUNTER': 1,
    # },
    # 'MQ03': {
    #     'CHANNEL': CHANNEL3,
    #     'DEFAULT_STATE': GPIO.PUD_DOWN,
    #     'EVENT': GPIO.RISING,
    #     'PART_COUNTER': 1,
    # },
    # 'MQ04': {
    #     'CHANNEL': CHANNEL4,
    #     'DEFAULT_STATE': GPIO.PUD_DOWN,
    #     'EVENT': GPIO.RISING,
    #     'PART_COUNTER': 1,
    # }
}

LED_PORT = 7 # Green LED indicator
SWITCH_DEBOUNCE_TIME = 2000 # in miliseconds
RESTART_PART_COUNTER = 10 # max units before restart

#############################
######## Server Setup #######
#############################

# Wiidem System's IP to connect the API
SERVER_IP = '201.235.179.124'
SERVER_PORT = 9012
SERVER_TIMEOUT = 3
# Wiidem Demo API
WIIDEM_DEMO_API = 'http://' + SERVER_IP + ':' + str(SERVER_PORT) + '/wiidem_pre_api/api/production/count'
# WIIDEM_DEMO_API = 'api/production/count'


###############################
####### Data Base Setup #######
###############################
# DB's name
DATABASE_FILE = 'gadget-' + str(GADGET_CODE) + '.db'


#############################
######### Log Setup #########
#############################
# Log Files
LOG_FILE_IO  = 'gadget-' + str(GADGET_CODE) + '-io.log'
LOG_FILE_API = 'gadget-' + str(GADGET_CODE) + '-api.log'

from lib.controller import *
from lib.apiclient import *
import time
import math
import sys
#import lib.fonts.fontMicro as font
#import lib.fonts.font4x6 as font
#import lib.fonts.font5x7 as font
import lib.fonts.font5x8 as font
#import lib.fonts.fontS5x8 as font

VERSION = 1.0

pico = Pico(font, True)
pico.setFunctionMode(IMUPLUS_MODE)
pico.setPowerMode(POWER_LOW)
OLED_STEP_HEIGHT = 8 #How much space each character takes length wise
OLED_STEP_WIDTH = 8 #How much space each character takes width wise

client = Client(VERSION, pico)

startTime = time.time_ns() #All time is in milliseconds
prevValues = dict() # Storage container for all previous values used by state change comparision functions

isRunning = False
hasClothes = False
doorOpen = False
prevValues['isRunning'] = False
prevValues['rotSpikes'] = 0
prevValues['doorOpen'] = False

NANTOMILCONVERSION = math.pow(10, 6)
DELAYSCREEN = 1 * 1000 # Time between screen updates in millis, first number is how many seconds
DELAYVALS = 200 # Time between reading gyro updates in millis
ITERCALC = 20 # Iterations of reading gyro updates before extrapolating data
DELAYSTOP = 2 * 60000 # Time required for isRunning to be false before updating the server in millis, first val is the number of minutes
DELAYRUN = 5000 # Time required for isRunning to be true before updating the server in millis

RUNTHRES = 0.4 # The linear acceleration thresholds before detecting a changed state (Arbitrarily set based on testing data)
ROTTHRES = 50.0 # The roational acceleration thresholds before detecting a changed state (Arbitrarily set based on testing data)

doPrint = False

def start() -> None:
    """Starts the program"""
    try:
        while(True):
            getVals()
            calc()
            checkUpdate()
            updateScreen()
    except:
        reboot()

def updateScreen() -> None:
    """Updates the Screen"""
    global isRunning, hasClothes, doorOpen
    prevUpdate = prevValues.get('screen')
    if not prevUpdate:
        prevUpdate = 0
    if getCurrentTime() - prevUpdate > DELAYSCREEN:
        pico.displayText(str(client.get_ID()) + " | " + prevValues.get('update'), 0, 0)
        pico.displayText(f"Running| Cur/A: {"T" if isRunning else "F"}/{"T" if prevValues.get('isRunning') else "F"}", 0, OLED_STEP_HEIGHT)
        pico.displayText(f"Clothes| H/O/C: {"T" if hasClothes else "F"}/{"T" if doorOpen else "F"}/{compact_number_with_ones(prevValues.get('rotSpikes'))}", 0, OLED_STEP_HEIGHT*2)
        
        # Print items without spaces to conserve space
        fullDataR = "["
        for val in prevValues['rot']:
            fullDataR += pico.formatValue(val) + ","
        fullDataR = fullDataR[0:fullDataR.rindex(",")]  # remove the last comma
        fullDataR += "]"

        pico.displayText(f"Rot: {fullDataR}", 0, OLED_STEP_HEIGHT * 3)
        prevValues['screen'] = getCurrentTime()

def getVals() -> None:
    """Updates gyro values\n
    Adds the absolute value of the current linear and rotational acceleration to compute average acceleration"""
    prevUpdate = prevValues.get('getVals')
    if not prevUpdate:
        prevUpdate = 0
    if getCurrentTime() - prevUpdate > DELAYVALS:
        rotVals = pico.getRotationalAcc()
        for i in range(0, 3):
            prevValues['rot'][i] = max(abs(rotVals[i]), prevValues['rot'][i])
        prevValues['iters'] += 1
        prevValues['getVals'] = getCurrentTime()

def calc() -> None:
    """Gets the average of gyro measurements in a set amount of iterations and changes the temporary state value accordingly"""
    global isRunning, hasClothes, doorOpen
    if prevValues['iters'] >= ITERCALC:
        if prevValues['rot'][0] >= ROTTHRES or prevValues['rot'][1] >= ROTTHRES or prevValues['rot'][2] >= ROTTHRES:
            prevValues['rotSpikes'] += 1
            doorOpen = not doorOpen
        else:
            if prevValues['rot'][0] >= RUNTHRES or prevValues['rot'][1] >= RUNTHRES or prevValues['rot'][2] >= RUNTHRES:
                isRunning = True
            else:
                isRunning = False     
        
        reset()

def reset() -> None:
    """Resets the values of all previous storage variables on calculation"""
    prevValues['iters'] = 0
    prevValues['rot'] = [float(0), float(0), float(0)]

def checkUpdate() -> None:
    """Checks for a change based on calc and updates accordingly\n
    Adds layer of verification to prevent incorrect changes"""
    global isRunning, hasClothes, doorOpen

    #Checking isRunning status
    if (not isRunning == prevValues['isRunning']) and ((prevValues['isRunning'] and getCurrentTime() - prevValues['checkRun'] > DELAYSTOP) or (not prevValues['isRunning'] and getCurrentTime() - prevValues['checkRun'] > DELAYRUN)):
        while(not client.set_isRunning(isRunning).ok()):
            if doPrint:
                print("Change Failed: isRunning")
        if doPrint:
            print(f"Changed isRunning from {prevValues['isRunning']} to {isRunning}")
        prevValues['isRunning'] = isRunning
        setUpdate()
    elif (not isRunning == prevValues['isRunning']) and doPrint:
        if prevValues['isRunning']:
            print(f"Time left before isRunning -> {isRunning} update: { DELAYSTOP - (getCurrentTime() -prevValues['checkRun'])}")
        else:
            print(f"Time left before isRunning -> {isRunning} update: { DELAYRUN - (getCurrentTime() -prevValues['checkRun'])}")
    elif isRunning == prevValues['isRunning']:
        prevValues['checkRun'] = getCurrentTime()

    # Checking hasClothes status
    if prevValues['isRunning'] and not hasClothes:
        hasClothes = True
        while(not client.set_hasClothes(hasClothes).ok()):
            if doPrint:
                print("Change Failed: hasClothes")
        if doPrint:
            print(f"Changed hasClothes from {not hasClothes} to {hasClothes} because isRunning")
        setUpdate()
    elif not prevValues['isRunning'] and prevValues['doorOpen'] and hasClothes:
        hasClothes = False
        while(not client.set_hasClothes(hasClothes).ok()):
            if doPrint:
                print("Change Failed: hasClothes")
        if doPrint:
            print(f"Changed hasClothes from {not hasClothes} to {hasClothes}")
        setUpdate()

    # Checking doorOpen Status
    if not prevValues['doorOpen'] == doorOpen:
        while(not client.set_doorOpen(doorOpen).ok()):
            if doPrint:
                print("Change Failed: doorOpen")
        if doPrint:
            print(f"Changed doorOpen to True")
        setUpdate()
        prevValues['doorOpen'] = doorOpen
    elif prevValues['isRunning'] and doorOpen:
        doorOpen = False
        while(not client.set_doorOpen(doorOpen).ok()):
            if doPrint:
                print("Change Failed: doorOpen")
        if doPrint:
            print(f"Changed doorOpen from {not doorOpen} to {doorOpen} because isRunning")
        setUpdate()
        if prevValues['rotSpikes'] % 2 == 1:
            prevValues['rotSpikes'] += 1

def reboot() -> None:
    pico.reset()

def setUpdate() -> None:
    prevValues['update'] = str(client.get_last_update())
    if not (prevValues['update'] == None):
        prevValues['update'] = prevValues['update'].replace("/", ":")

def getCurrentTime() -> int:
    """Returns the current time since program start in nanoseconds"""
    return (time.time_ns() - startTime)/NANTOMILCONVERSION

def compact_number_with_ones(n: int) -> str:
    """
    Returns a compact string representation of a number that includes 
    the thousands or millions abbreviation and conserves the ones place.
    """
    if n < 1000:
        return str(n)
    elif 1000 <= n < 1_000_000:
        # For numbers in the thousands range
        thousands = n // 1000
        ones = n % 10
        return f"{thousands}K{ones}"
    elif n >= 1_000_000:
        # For numbers in the millions range
        millions = n // 1_000_000
        ones = n % 10
        return f"{millions}M{ones}"
    else:
        return str(n)

reset()
setUpdate()
start()
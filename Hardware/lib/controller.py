from lib.imu6050 import MPU6050
import time
from machine import Pin, I2C, SoftI2C
import lib.OLED as OLED
from lib.bno055 import *
from math import pow
from ezFont import ezFBfont

OLED_WIDTH = 128 #Pixel Width of the OLED
OLED_HEIGHT = 32 #Pixel Height of the OLED

#Power Modes
POWER_NORMAL = const(0x00)
POWER_LOW = const(0x01)
POWER_SUSPEND = const(0x02)
#Power Register for writing
POWER_REGISTER = const(0x3e)

#Function Modes
IMUPLUS_MODE = const(0x08)
NDOF_MODE = const(0x0c)

class Pico:

    def __init__(self, font, isBNO = False):
        """Creates a pico object.
        isBNO must be set to true if using the BNO055, otherwise will use MPU6050"""
        #Initializing the onboard light
        self.LED = Pin("LED", Pin.OUT)
        #Initializing the OLED
        self.oled = ezFBfont(OLED.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, SoftI2C(sda=Pin(2), scl=Pin(3)), addr=0x3c), font)
        #Initializing the MPU (bno or 6050)
        self.bno = isBNO
        i2cGyro = I2C(0, sda=Pin(4), scl=Pin(5))
        if(self.bno):
            self.imu = BNO055(i2cGyro)
        else:
            self.imu = MPU6050(i2cGyro)

    def setLED(self, boolOn) -> None:
        """Turns the LED on or off"""
        if(boolOn):
            self.LED.on()
        else:
            self.LED.off()

    def __updateGyro(self) -> tuple:
        """Returns a tuple of lists of the linear accel values, gyro values, and temperature.
        Automatically accounts for running either the BNO055 or MPU6050 code."""
        if(self.bno):
            gyroVals = self.imu.gyro()
            accelVals = self.imu.lin_acc()
            return ([accelVals[0], accelVals[1], accelVals[2]], [gyroVals[0], gyroVals[1], gyroVals[2]], [self.imu.temperature()])
        else:
            return ([self.imu.accel.x, self.imu.accel.y, self.imu.accel.z], [self.imu.gyro.x, self.imu.gyro.y, self.imu.gyro.z], [self.imu.temperature()])

    def getLinearAcc(self) -> list:
        """Returns a list containing the linear acceleration values in 3 dimensions"""
        return self.__updateGyro()[0]
    
    def getRotationalAcc(self) -> list:
        """Returns a list containing the rotational acceleration values in 3 dimensions."""
        return self.__updateGyro()[1]

    def getTemperature(self) -> float:
        """Returns a float value for the temperature"""
        return self.__updateGyro()[2][0]

    def getCompass(self) -> list:
        """pre: Must have set isBNO to true\n
        Returns the yaw, pitch, and roll.\n
        Only works is the imu is the bno"""
        if not self.bno:
            raise TypeError("Currently set to use MPU6050. This function only works for BNO055")
        euler = self.imu.euler()
        return [euler[0], euler[1], euler[2]]

    def getCompassF(self) -> list:
        """pre: Must have set isBNO to true\n
        Returns a list of strings of the bno compass values formatted as: 00.000"""
        values = self.bnoCompass()
        return [self.__formatValue(values[0]), self.__formatValue(values[1]), self.__formatValue(values[2])]

    def formatValue(self, val):
        if val >= 10 or val <= -10:
            return f"{val:5.1f}"[:5]  # Two digits before decimal, one after for negative numbers with sign
        elif val >= 0:
            return f"{val: 5.2f}"  # Extra space for single-digit positive numbers with two decimal places
        else:
            return f"{val:05.2f}"[:5]  # Negative numbers take one space for the sign, two decimal places

    def setPowerMode(self, Mode) -> None:
        """pre: Must have set isBNO to true\n
        Sets the BNO055's power mode\n
        Used to make the bno more power efficient\n
        Modes: Can be found above\n
        Only works is the imu is the bno"""
        if not self.bno:
            raise TypeError("Currently set to use MPU6050. This function only works for BNO055")
        self.imu._write(POWER_REGISTER, Mode)
        
    def setFunctionMode(self, Mode) -> None:
        """pre: Must have set isBNO to true\n
        Sets the BNO055's function mode\n
        Used to turn of certain parts for power efficiency\n
        Modes: IMUPLUS_MODE [Only gyro and accel], NDOF_MODE [Everything]\n
        Only works is the imu is the bno"""
        if not self.bno:
            raise TypeError("Currently set to use MPU6050. This function only works for BNO055")
        self.imu.mode(Mode)

    def displayText(self, text, x, y) -> None:
        """pre: text must be a string
        Displays text on screen at the specified x and y positions"""
        if type(text) is not str:
            raise TypeError("Text must be a string")
        self.oled.write(text, x, y)
        self.oled.show()
            
    def picoWait(self, delay) -> None:
        """Stops the pico for the given time in milliseconds"""
        MILLTOSECCONVERSION = pow(10, 3)
        time.sleep(delay/MILLTOSECCONVERSION)

    def reset(self):
        machine.reset()

    def clearScreen(self) -> None:
        """Clear the Screen by setting everything to spaces"""
        self.oled.fill(0)
        self.oled.show()
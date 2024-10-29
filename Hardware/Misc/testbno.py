import machine
import time
from lib.bno055 import *

#Constants
_POWER_NORMAL = const(0x00)
_POWER_LOW = const(0x01)
_POWER_SUSPEND = const(0x02)
_POWER_REGISTER = const(0x3e)

i2c = machine.I2C(0, sda=machine.Pin(4), scl=machine.Pin(5))

imu = BNO055(i2c)
#calibrated = False

# Set to IMU Plus mode (accelerometer + gyroscope, no magnetometer)
imu.mode(IMUPLUS_MODE)

# Switch to Low Power Mode
imu._write(_POWER_REGISTER, _POWER_LOW)

while True:
    time.sleep(0.05)
    print('Gyro (Rot Accel) x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.gyro()))
    print('Heading     {:4.0f} roll {:4.0f} pitch {:4.0f}'.format(*imu.euler()))
    print('Lin acc.  x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.lin_acc()))
    '''print('Accel     x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.accel()))
    print('Gravity   x {:5.1f}    y {:5.1f}     z {:5.1f}'.format(*imu.gravity()))
    print('Temperature {}°C'.format(imu.temperature()))
    print('Mag       x {:5.0f}    y {:5.0f}     z {:5.0f}'.format(*imu.mag()))
    if not calibrated:
        calibrated = imu.calibrated()
        print('Calibration required: sys {} gyro {} accel {} mag {}'.format(*imu.cal_status()))'''
    
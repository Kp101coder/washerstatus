# I2C Scanner MicroPython
from machine import Pin, SoftI2C

# You can choose any other combination of I2C pins
i2c = SoftI2C(sda=Pin(2), scl=Pin(3)) #LED pins

print('I2C SCANNER')
led = Pin("LED", Pin.OUT)
led.toggle()
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:', len(devices))

  for device in devices:
    print("I2C hexadecimal address: ", hex(device))
led.toggle()
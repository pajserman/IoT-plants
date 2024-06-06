from machine import Pin
import time
from dht import DHT11


waetherPin = Pin(27, Pin.OUT, Pin.PULL_DOWN)
weatherSensor = DHT11(waetherPin)

lightPin = Pin(15, Pin.IN, Pin.PULL_DOWN)

while True:
    weatherSensor.measure()
    tempC = weatherSensor.temperature()
    humidity = weatherSensor.humidity()
    sunshine = 1 if lightPin.value() == 0 else 0
    data = [tempC, humidity, sunshine]
    print(data)
    time.sleep(20)
import machine
from machine import Pin
from machine import PWM
import time
from dht import DHT11
import keys
import network
from umqttsimple import MQTTClient
import ubinascii
import json

# setup tone generator
buzzer = PWM(Pin(5))
buzzer.freq(2093)
buzzer.duty_u16(0)


# Pin variables
waetherPin = Pin(27, Pin.OUT, Pin.PULL_DOWN)
weatherSensor = DHT11(waetherPin)
lightPin = Pin(15, Pin.IN, Pin.PULL_DOWN)
led = Pin("LED", machine.Pin.OUT)

# WIFI variables
ssid, password = keys.WIFI_SSID, keys.WIFI_PASS

# MQTT variables
MQTT_BROKER = "192.168.1.226"
MQTT_TOPIC_TEMP = "Pico/sensor/Temperature"
MQTT_TOPIC_HUMIDITY = "Pico/sensor/Humidity"
MQTT_TOPIC_SUNSHINE = "Pico/sensor/Sunshine"
MQTT_TOPIC_SENSOR = "Pico/sensor"

# wlan needs to be global, defined outside of function
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def connect_to_wifi():
    led.on()
    limit = 0
    wlan.connect(ssid, password)
    while (wlan.isconnected() == False):
        print("Waiting for connection...")
        limit += 1
        if (limit > 10):
            limit = 0
            print("Time limit reached. Trying again...")
            wlan.connect(ssid, password)
        time.sleep(1)
    led.off()
    print("Connected to WIFI", "IP Adress is: " + wlan.ifconfig()[0])


# Connecting to WIFI
connect_to_wifi()

# setup MQTTClient
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_client = MQTTClient(client_id, MQTT_BROKER)
mqtt_client.connect()


def gather_data():
    weatherSensor.measure()
    tempC = weatherSensor.temperature()
    hum = weatherSensor.humidity()
    sun = (lightPin.value() + 1) % 2
    data = {'temperature': tempC, 'humidity': hum, 'sunshine': sun}
    return data


# THE MAIN LOOP
while (True):
    while (wlan.isconnected() == True):
        data = gather_data()  # data {temp, hum, sun}
        print(data)

        # sounding alarm if sun is to intense
        if (data['sunshine'] == 0):
            buzzer.duty_u16(1000)
        else:
            buzzer.duty_u16(0)

        # publish data
        led.toggle()
        # mqtt_client.publish(MQTT_TOPIC_TEMP, data['temperature'])
        # mqtt_client.publish(MQTT_TOPIC_HUMIDITY, data['humidity'])
        # mqtt_client.publish(MQTT_TOPIC_SUNSHINE, data['sunshine'])

        json_string = json.dumps(data)
        mqtt_client.publish(MQTT_TOPIC_SENSOR, json_string)
        led.toggle()
        time.sleep(5)
    else:
        connect_to_wifi()

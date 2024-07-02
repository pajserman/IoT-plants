import machine
from machine import Pin
import time
from dht import DHT11
import keys
import network
from umqttsimple import MQTTClient
import ubinascii
import json


# Pin variables
waetherPin = Pin(27, Pin.OUT, Pin.PULL_DOWN)
weatherSensor = DHT11(waetherPin)

# using the built in LED as an indicator:
# ON=connecting to WIFI, fast ON/OFF=sent/sending data
led = Pin("LED", machine.Pin.OUT)

# WIFI variables
ssid, password = keys.WIFI_SSID, keys.WIFI_PASS

# MQTT variables
MQTT_BROKER = "192.168.1.226"
MQTT_TOPIC_SENSOR = "Pico/sensor"
MQTT_TOPIC_ERROR_COLLECTING = "Pico/error/collecting"
MQTT_TOPIC_ERROR_OTHER = "Pico/error/other"
collecting = 0
other = 0


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
    data = {'temperature': tempC, 'humidity': hum}
    return data


# THE MAIN LOOP
while (True):
    try:
        while (wlan.isconnected() == True):
            try:
                data = gather_data()  # data {temp, hum}
                print(data)
            except:
                collecting += 1
                mqtt_client.publish(
                    MQTT_TOPIC_ERROR_COLLECTING, str(collecting))
                print("Something went wrong in collecting data sleeping 5 ...")
                time.sleep(5)

            # publish data
            led.toggle()
            json_string = json.dumps(data)
            mqtt_client.publish(MQTT_TOPIC_SENSOR, json_string)
            led.toggle()
            time.sleep(5)
        else:
            connect_to_wifi()
    except:
        other += 1
        mqtt_client.publish(MQTT_TOPIC_ERROR_OTHER, str(other))
        print("Something went wrong in collecting data sleeping 5 ...")
        time.sleep(5)

import paho.mqtt.client as mqtt
from random import randrange, uniform
import time

mqttBroker = "mqtt.eclipseprojects.io"

client = mqtt.Client("Medical")
client.connect(mqttBroker)

while True:
    randNumber = randrange(20)
    client.publish("TUBE", randNumber)
    print("Just published " + str(randNumber) + " to topic TUBE")
    time.sleep(1)

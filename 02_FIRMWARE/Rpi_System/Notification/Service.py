import threading
import time
import paho.mqtt.client as mqtt


class MQTT:
    def __init__(self, broker="broker.mqttdashboard.com", client_id="clientId-180d92Hh8z"):
        self.broker = broker
        self.client_id = client_id
        self.client = mqtt.Client(self.client_id)
        self.message = ''
        self.t_listener = None
        self.t_sender = None

    def connect(self):
        self.client.connect(self.broker)
        self.__listen__()

    def on_message(self, client, userdata, message):
        self.message = str(message.payload.decode("utf-8"))
        print("received message: {}".format(self.message))

    def __listen__(self, topic='TUBE', wait=30):

        self.client.subscribe(topic)
        self.client.on_message = self.on_message

        time.sleep(wait)
        self.client.loop_stop()

    def send(self, string, wait=1):
        self.client.publish(string)
        time.sleep(wait)

    # def start_listener(self):
    #     self.t_listener = threading.Thread(target=self.__listen__)

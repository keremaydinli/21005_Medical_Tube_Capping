from Service import MQTT
import time

mqtt1 = MQTT("mqtt.eclipseprojects.io", "R-2")
# mqtt2 = MQTT()
# mqtt2.connect()


if __name__ == "__main__":
    mqtt1.connect()
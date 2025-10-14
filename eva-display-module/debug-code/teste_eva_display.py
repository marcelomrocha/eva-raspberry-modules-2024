# Software developed by Marcelo Marques da Rocha
# MidiaCom Laboratory - Universidade Federal Fluminense
# This work was funded by CAPES and Google Research

from paho.mqtt import client as mqtt_client

import tkinter as tk
from PIL import Image, ImageTk
from itertools import count

import random
import time

import sys

sys.path.append('/home/pi/EVA_ROBOT')

import config # Module with network device configurations.

broker = config.MQTT_BROKER_ADRESS # Broker address.
port = config.MQTT_PORT # Broker Port.
topic_base = "EVA" # config.EVA_TOPIC_BASE



# MQTT
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # Reconnect then subscriptions will be renewed.
    pass
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Mensagem")

            
# Run the MQTT client thread.
client = mqtt_client.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect(broker, port)
    print(broker, port)
except:
    print ("Unable to connect to Broker.")
    exit(1)

# You cannot use the "forever" method (as in other modules) because it blocks not allowing
# for the graphical interface thread loop to execute.
client.loop_start()

messages = ["NEUTRAL", "HAPPY", "SAD", "ANGRY", "DISGUST", "INLOVE", "FEAR", "SURPRISE"]

while(1):
    index1 = 0
    client.publish("EVA" + '/evaEmotion', messages[index1])
    time.sleep(1.5)
    index2 = random.randint(0, 7)
    index3 = random.randint(0, 7)
    client.publish("EVA" + '/evaEmotion', messages[index2]) 
    client.publish("EVA" + '/evaEmotion', messages[index3]) 
    client.publish("EVA" + '/evaEmotion', messages[index2]) 
    client.publish("EVA" + '/evaEmotion', messages[index3]) 
    print(messages[index2], messages[index3])
    time.sleep(1)






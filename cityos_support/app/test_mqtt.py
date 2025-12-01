import time
import json
import threading

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

from env import mqtt_broker, mqtt_port

def on_connect(client, userdata, flag, rc, propertie):
    try:
        if rc == 0:
            print('conneced to MQTT broker')
        else:
            print('fail to connect', e)

    except Exception as e:
        print('on_connect', e)

def on_message(client, userdata, msg):
    try:
        text = str(msg.payload.decode())
        print('MQTT 受信データ', msg.topic, text)

    except Exception as e:
        print('on_message', e)

stop_event = threading.Event()

def subscribe_thread(client, topic):
    try:
        print('subscribe loop start')
        client.subscribe(topic)
        client.loop_start()
        stop_event.wait()
        client.loop_stop()
        client.disconnect()
        print('subscribe loop disconnected')
        
    except Exception as e:
        print('subscribe_thread', e)

class TestMQTT:

    MYNAME = 'MQTT_TEST'

    @classmethod
    def stop_subscribe(cls):
        try:
            print('stop subscribe loop...')
            stop_event.set()

        except Exception as e:
            print('stop_subscribe', e)

    def connect_mqtt(self, username, password):
        result = None
        try:
            print('connect_mqtt called')
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.MYNAME)
            client.username_pw_set(username, password)
            client.on_connect = on_connect
            client.on_message = on_message

            print(mqtt_broker, mqtt_port)
            client.connect(mqtt_broker, mqtt_port, 60)
            result = client

        except Exception as e:
            print('ERROR: connect_mqtt', e)
        return result
       
    def publish(self, username, password, topic, data):
        result = False
        try:
            print('MQTT publish', username, password, topic, data)
            client = self.connect_mqtt(username, password)
            if client is not None:
                payload = json.dumps(data)
                r = client.publish(topic, payload)
                status = r[0]
                if status == 0:
                    print('送信しました')
                else:
                    print('送信に失敗しました')
            else:
                print('MQTT connect failed')

        except Exception as e:
            print('publish', e)
        return result

    def subscribe(self, topic, username, password):
        result = False
        try:
            client = self.connect_mqtt(username, password)
            if client is not None:
                stop_event.clear()

                sub_thread = threading.Thread(target=subscribe_thread, args=(client,topic, ))
                sub_thread.start()
                sub_thread.join()
                print('end of subscribe loop')
            else:
                print('can not create mqtt client')

        except Exception as e:
            print('subscribe', e)
        return result
    

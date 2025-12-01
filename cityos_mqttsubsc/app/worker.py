import paho.mqtt.client as mqtt

import threading
import queue
import time
import datetime
import json

from datastore import DataStore

from env import mqtt_admin_user, mqtt_admin_pass, mqtt_broker, mqtt_port

class Worker(mqtt.Client):
    CLIENT_ID = 'CITYOS_MQTT_SUBSCRIBER'
    TIMESTAMP_FIELD = '_updated_at'

    def __init__(self):
        super().__init__(client_id=self.CLIENT_ID)
        try:
            self.queue = None
            self.client_id = 'cityos_mqtt_subscriber'
            self.qos = 0
            self.topic_pattern = '#'

            delta = datetime.timedelta(hours=9)
            self.JST = datetime.timezone(delta, 'JST')

        except Exception as e:
            print('Worker.init', e)

    def on_connect(self, client, obj, flag, rc):
        try:
            if rc == 0:
                print('connected to MQTT broker')
            else:
                print('fail to connect', rc)
        except Exception as e:
            print('on_connect', e)

    def on_message(self, client, obj, msg):
        result = False
        try:
            topic_id = msg.topic
            if not topic_id.startswith("$SYS/"):
                doc = json.loads(msg.payload)
                
                # データ受信時刻を記録する
                now = datetime.datetime.now(self.JST)
                nowtime = now.isoformat()   # formatしないほうが効率がいいか？
                                            # データを見るときはformatして欲しい・・
                doc[self.TIMESTAMP_FIELD] = nowtime

                data = {
                    'topic': topic_id,
                    'doc': doc
                }
                print('data', data)

                self.queue.put(data)
                result = True
            else:
                print('管理用メッセージを受信', topic_id)

        except Exception as e:
            print('on_message', e)
        return result

    def start_subscriber(self):
        result = 0
        try:
            print('subscriber start...')
            self.stop_event = threading.Event()

            # 子との通信用キューを作成
            self.queue = queue.Queue()
            print('make child')
            self.child = DataStore(self.queue)
            if self.child is not None:
                self.child.start()
                self.username_pw_set(mqtt_admin_user, mqtt_admin_pass)

                # TLS
                """
                self.tls_set(
                    ca_certs='./certs/tls/ca-root-cert.crt', certfile=None, keyfile=None,
                    tls_version=ssl.PROTOCOL_TLSv1_2,
                    cert_reqs=ssl.CERT_NONE,
                    ciphers=None)

                self.tls_insecure_set(True)
                """
                self.connect(mqtt_broker, port=mqtt_port, keepalive=60)
                self.subscribe(self.topic_pattern, qos=self.qos)
                self.loop_start()
                print('MQTT loop started')
            else:
                print('データストアを作成できません')

        except Exception as e:
            print('start_subscriber', e)

        return result

    def stop_subscriber(self):
        result = False
        try:
            # normal stop process for child
            if hasattr(self, 'child') and self.child:
                self.queue.put(None)
                self.child.force_stop = True
                self.child.join()

            self.stop_event.set()
            self.loop_stop()
            self.disconnect()
            print('subscriber stopped')
            result = True
        
        except Exception as e:
            print('stop_subscriber', e)
        
        return result

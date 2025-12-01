import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import threading
import queue
import ctypes
import time
import datetime
import requests

from myconfig import MyConfig
from env import orion_server

class DataStore(threading.Thread):

    orion_version = 'v2'
    api_timeout = 10
    force_stop = False
    myconfig_dict = {}

    ua = 'BODIK/2.0'
    post_headers = {
        #'Fiware-Service': fiware_service,
        #'Fiware-ServicePath':fiware_service_path,
        'User-Agent': ua,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    fiware_datatype_dict = {
        'Lgcode': 'Text',
        'Lgname': 'Text',
        'Keyword': 'Text',
        'String': 'Text',
        'List': 'Array',
        'Integer': 'Number',
        'Float': 'Number',
        'Date': 'date',     # 2024-03-27 Numberになっていた。dateに修正
        'Time': 'time',
        'Address': 'Text',
        'Tel': 'Text',
        'Url': 'URL',
        'Umu': 'Text',
        'Kahi': 'Text',
        'Location.lat': 'Number',
        'Location.lon': 'Number',
    }

    def __init__(self, queue):
        super(DataStore, self).__init__()
        try:
            self.queue = queue
            self.wait_sec = 10
            self.objConfig = MyConfig()
            self.myconfig = None
            self.myconfig_dict = {}

            delta = datetime.timedelta(hours=9)
            self.JST = datetime.timezone(delta, 'JST')

        except Exception as e:
            print('DataStore.init', e)
    
    # threadクラスで、start後、内部的に呼び出される予約されたメソッド
    def run(self):
        result = False
        try:
            self.id = threading.get_native_id()
            active = True
            while active:
                try:
                    data = self.queue.get(block=True)
                    if data is None:
                        # 停止命令
                        break

                    print('received data', data)
                    self.copy_data_to_orion(data)

                except Exception as e:
                    if self.force_stop:
                        active = False

            result = True

        except Exception as e:
            print('run', e)
        
        print('DataStoreを停止しました')
        return result

    def copy_data_to_orion(self, data):
        result = False
        try:
            if 'topic' in data and 'doc' in data:
                topic_id = data['topic']
                doc = data['doc']

                myconfig = None
                if topic_id in self.myconfig_dict:
                    myconfig = self.myconfig_dict[topic_id]
                else:
                    myconfig = self.objConfig.get_entity_config(topic_id)
                    self.myconfig_dict[topic_id] = myconfig    # Noneの場合も記録する
                
                if myconfig is not None:
                    self.myconfig = myconfig
                    self.entity_type = myconfig['entity_type']
                    self.service = myconfig['Fiware-Service']
                    self.service_path = myconfig['Fiware-ServicePath']
                    if self.service is not None and self.service_path is not None:
                        self.post_headers['Fiware-Service'] = self.service
                        self.post_headers['Fiware-ServicePath'] = self.service_path

                    doc = self.make_doc(doc)
                    if doc is not None:
                        url = f'{orion_server}/{self.orion_version}/entities?options=upsert'
                        r = requests.post(url, json=doc, headers=self.post_headers, timeout=self.api_timeout, verify=False)
                        if r.status_code == 201:    # 新規作成成功
                            result = True
                        elif r.status_code == 204:  # 更新成功
                            result = True
                        else:
                            print('status_code', r.status_code)

                else:
                    print('MyAPIに登録されていません', topic_id)
            else:
                print('フォーマット違反です', data)

        except Exception as e:
            print('save_data', e)
        return result

    def make_id(self, data):
        result = None
        try:
            uid = f'{self.entity_type}'
            fields = self.myconfig['key']['fiware']['fields']
            for fld in fields:
                uid = f'{uid}.{data[fld]}'
            result = uid

        except Exception as e:
            print('make_id', e)
        return result
    
    def make_doc(self, data):
        result = None
        try:
            uid = self.make_id(data)
            doc = {
                'id': uid,
                'type': self.entity_type,
            }

            dataModel = self.myconfig['dataModel']
            for field in dataModel:
                info = dataModel[field]
                field_name = info['field_name']
                data_type = info['type']
                if data_type in self.fiware_datatype_dict:
                    data_type = self.fiware_datatype_dict[data_type]
                else:
                    data_type = 'Text'
                
                value = None
                if field in data:
                    value = data[field]
                
                doc[field_name] = {
                    'type': data_type,
                    'value': value
                }

            geometry = self.myconfig['geometry']
            if geometry == 'Point':
                lat = None
                lon = None
                if 'lat' in doc:
                    lat = doc['lat']['value']
                if 'lon' in doc:
                    lon = doc['lon']['value']

                if lat is not None and lon is not None:
                    doc['location'] = {
                        'type': 'geo:json',
                        'value': {
                            'type': 'Point',
                            'coordinates': [ lon, lat]
                        }
                    }
                
                    del doc['lat']
                    del doc['lon']

            result = doc

        except Exception  as e:
            print('make_doc', e)
        return result


import threading
import queue
import ctypes
import time
import datetime

import myes
from myconfig import MyConfig

class Worker(threading.Thread):

    TIMESTAMP_FIELD = '_updated_at'

    def __init__(self, queue):
        super(Worker, self).__init__()
        try:
            self.queue = queue
            self.objConfig = MyConfig()
            self.myconfig_dict = {}

            delta = datetime.timedelta(hours=9)
            self.JST = datetime.timezone(delta, 'JST')

        except Exception as e:
            print('Worker.init', e)

    """
    def stop(self):
        try:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.id), 
                ctypes.py_object(SystemExit)
            )
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(self.id), 
                    0
                )
                print('Failure in raising exception')

        except Exception as e:
            print('Exception stop failed', e)
    """

    def run(self):
        try:
            self.id = threading.get_native_id()
            working = True
            while working:
                try:
                    info = self.queue.get(block=True)
                    if info is not None:
                        self.parse(info)
                        self.queue.task_done()
                    else:
                        print('stop command received')
                        working = False

                except queue.Empty:
                    pass
            
            print('exit worker loop')
        
        except Exception as e:
            print('Worker.run', e)

    def parse(self, info):
        result = False
        try:
            print('サブスクリプションで受け取った', info)
            usecase = info['usecase']
            payload = info['data']

            for data in payload['data']:
                entity_type = data['type']
                myconfig = self.get_entity_config(entity_type)
                if myconfig is not None:
                    # indexが指定されていたら、履歴化対象とみなす
                    if 'index' in myconfig and myconfig['index'] != '':
                        self.save_data(myconfig, data)

        except Exception as e:
            print('parse', e)
        return result

    def get_entity_config(self, entity_type):
        result = None
        try:
            myconfig = None
            if entity_type in self.myconfig_dict:
                myconfig = self.myconfig_dict[entity_type]
            else:
                myconfig = self.objConfig.get_entity_config(entity_type)
                if myconfig is not None:
                    print('myconfig', myconfig)
                    self.myconfig_dict[entity_type] = myconfig
                    # ESのインデックスを作成する
                    myes.create_index(myconfig)
                    time.sleep(1)
                else:
                    print('can not get myconfig', entity_type)
            
            result = myconfig

        except Exception as e:
            print('get_entity_myconfig', e)
        return result
    
    def save_data(self, myconfig, data):
        result = False
        try:
            # 履歴DB登録情報があれば、履歴DBに登録する
            if 'key' in myconfig and 'es' in myconfig['key'] and 'fields' in myconfig['key']['es']:
                doc_id = myconfig['apiname']
                fields = myconfig['key']['es']['fields']
                for field in fields:
                    doc_id = f'{doc_id}.{data[field]}'

                data_fields = myconfig['fields']
                doc = {}
                for field in data_fields:
                    if field in data:
                        info = data_fields[field]
                        value = data[field]
                        # Orionとelasticsearchでは緯度経度情報の持ち方が異なる
                        if info['field_type'] == 'Point':
                            # 緯度経度情報をelasticsearchに合わせて読み替える
                            coord = value['coordinates']
                            doc[field] = {
                                'lat': coord[1],
                                'lon': coord[0]
                            }
                        else:
                            doc[field] = value

                if self.TIMESTAMP_FIELD not in doc:
                    # ソート用に登録時刻を記録する
                    now = datetime.datetime.now(self.JST)
                    nowtime = now.isoformat()
                    doc[self.TIMESTAMP_FIELD] = nowtime

                #print('create_document', doc_id, doc)
                myes.create_document(myconfig, doc_id, doc)
                result = True
            else:
                print('履歴のID情報がセットされていません', myconfig)

        except Exception as e:
            print('save_data', e)
        return result
    
    def decodeFiwareEscapeChar(self, text):
        result = None
        try:
            result = text

            decode_list = {
                '%3C': '<',
                '%3E': '>',
                '%22': '"',
                "%27": "'",
                '%3D': '=',
                '%3B': ';',
                '%28': '(',
                '%29': ')',
                '%25': '%',     # 最後に処理する
            }

            converted = text
            for ch in decode_list:
                converted = converted.replace(ch, decode_list[ch])
            
            if converted != text:
                result = converted

        except Exception as e:
            print('decodeFiwareEscapeChar', e)
        
        return result

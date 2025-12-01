import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import requests
import json

from myconfig import MyConfig
from env import orion_server

class TestOrion:

    orion_version = 'v2'
    ua = 'BODIK/2.0'
    api_timeout = 10

    get_headers = {
        #'Fiware-Service': fiware_service,
        #'Fiware-ServicePath':fiware_service_path,
        'User-Agent': ua,
        'Accept': 'application/json'
    }
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

    def __init__(self, apiname):
        try:
            obj = MyConfig()
            myconfig = obj.get_config(apiname)
            if myconfig is not None:
                self.myconfig = myconfig
                self.entity_type = myconfig['entity_type']
                self.service = myconfig['Fiware-Service']
                self.service_path = myconfig['Fiware-ServicePath']
                if self.service is not None and self.service_path is not None:
                    self.get_headers['Fiware-Service'] = self.service
                    self.get_headers['Fiware-ServicePath'] = self.service_path
                    self.post_headers['Fiware-Service'] = self.service
                    self.post_headers['Fiware-ServicePath'] = self.service_path

        except Exception as e:
            print('TestIrion.init', e)

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
    
    def set_data(self, data):
        result = False
        try:
            uid = self.make_id(data)
            url = f'{orion_server}/{self.orion_version}/entities?options=upsert'
            print('url', url)
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

            print('doc', doc)
            print('headers', self.post_headers)
            r = requests.post(url, json=doc, headers=self.post_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 201:    # 新規作成成功
                result = True
            elif r.status_code == 204:  # 更新成功
                result = True
            else:
                print('status_code', r.status_code)

        except Exception  as e:
            print('set_data', e)
        return result

    def get_data(self, id):
        result = None
        try:
            url = f'{orion_server}/{self.orion_version}/entities/{id}'
            r = requests.get(url, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 200:
                data = r.json()
                result = data
            else:
                print('status_code', r.status_code)

        except Exception  as e:
            print('get_data', e)
        return result

    def search_data(self):
        result = None
        try:
            url = f'{orion_server}/{self.orion_version}/entities'
            count = 100
            q = {
                'type': self.entity_type,
                'options': 'keyValues',
                'offset': 0,
                'limit': count
            }
            r = requests.get(url, params=q, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 200:
                data = r.json()
                result = data
            else:
                print('status_coed', r.status_code)

        except Exception  as e:
            print('search_data', e)
        return result

    def delete_all_data(self):
        result = False
        try:
            url = f'{orion_server}/{self.orion_version}/entities'
            del_url = f'{orion_server}/{self.orion_version}/op/update'
            q = {
                'type': self.entity_type,
                'offset': 0,
                'limit': 100
            }
            r = requests.get(url, params=q, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 200:    # 新規作成成功
                data = r.json()
                
                entities = []
                for item in data:
                    info = {
                        'id': item['id']
                    }
                    entities.append(info)
                print('delete data', entities)

                body = {
                    'actionType': 'delete',
                    'entities': entities
                }
                r = requests.post(del_url, data=json.dumps(body), headers=self.post_headers, timeout=self.api_timeout, verify=False)
                if r.status_code == 204:
                    print('delete success')
                    result = True
                else:
                    print('delete status_code', r.status_code)

            else:
                print('status_code', r.status_code)

        except Exception  as e:
            print('set_data', e)
        return result

    def get_version(self):
        result = None
        try:
            url = f'{orion_server}/version'
            print('url', url)
            r = requests.get(url, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 200:
                data = r.json()
                result = data
            else:
                print('status_code', r.status_code)

        except Exception  as e:
            print('get_version', e)
        return result


import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import requests

from env import orion_server

class TestOrion:

    orion_version = 'v2'
    entity_type = "temperature"
    ua = 'BODIK/2.0'
    fiware_service = 'bodik'
    fiware_service_path = '/bodik'
    api_timeout = 10

    get_headers = {
        'Fiware-Service': fiware_service,
        'Fiware-ServicePath':fiware_service_path,
        'User-Agent': ua,
        'Accept': 'application/json'
    }
    post_headers = {
        'Fiware-Service': fiware_service,
        'Fiware-ServicePath':fiware_service_path,
        'User-Agent': ua,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    def set_data(self, id, value):
        result = False
        try:
            url = f'{orion_server}/{self.orion_version}/entities?options=upsert'
            data = {
                'id': id,
                'type': self.entity_type,
                'value': {
                    'type': 'Float',
                    'value': value
                }
            }
            r = requests.post(url, json=data, headers=self.post_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 201:    # 新規作成成功
                result = True
            elif r.status_code == 204:  # 更新成功
                result = True
            else:
                print('status_coed', r.status_code)

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
                print('status_coed', r.status_code)

        except Exception  as e:
            print('get_data', e)
        return result

    def search_data(self):
        result = None
        try:
            url = f'{orion_server}/{self.orion_version}/entities'
            qs = {
                'type': self.entity_type,
                'offset': 0,
                'limit': 100
            }
            r = requests.get(url, params=qs, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 200:
                data = r.json()
                
                entities = []
                for item in data:
                    entities.append(item['id'])

                body = {
                    'actionType': 'delete',
                    'entities': entities
                }
                r = requests.post(url, data=body, headers=self.post_headers, timeout=self.api_timeout, verify=False)
                if r.status_code == 204:
                    result = True

            else:
                print('status_coed', r.status_code)

        except Exception  as e:
            print('search_data', e)
        return result

    def delete_all_data(self):
        result = False
        try:
            url = f'{orion_server}/{self.orion_version}/entities'
            qs = {
                'type': self.entity_type,
            }
            r = requests.get(url, params=qs, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 201:    # 新規作成成功
                result = True
            elif r.status_code == 204:  # 更新成功
                result = True
            else:
                print('status_coed', r.status_code)

        except Exception  as e:
            print('set_data', e)
        return result

    def get_version(self):
        result = None
        try:
            headers = {
                'User-Agent': self.ua,
                'Accept': 'application/json'
            }

            url = f'{orion_server}/version'
            r = requests.get(url, headers=headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 200:
                data = r.json()
                result = data
            else:
                print('status_coed', r.status_code)

        except Exception  as e:
            print('get_version', e)
        return result


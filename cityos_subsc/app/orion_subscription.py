import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import requests
import json

from myconfig import MyConfig
from env import orion_server

class OrionSubscription:

    def __init__(self, usecase, apiname):
        try:
            self.apiname = apiname
            self.usecase = usecase
            self.subscription_key = f'{usecase}|{apiname}'
            self.orion_server = f'{orion_server}/v2'
            self.api_timeout = 10.0
            self.subscription_list = None

            obj = MyConfig()
            self.myconfig = obj.get_config(apiname)
            print('myconfig', apiname, self.myconfig)
            if self.myconfig is not None:
                self.entity_type = self.myconfig['entity_type']
                self.get_headers = {
                    'Fiware-Service': self.myconfig['Fiware-Service'],
                    'Fiware-ServicePath': self.myconfig['Fiware-ServicePath']
                }
                self.post_headers = {
                    'Content-Type': 'application/json',
                    'Fiware-Service': self.myconfig['Fiware-Service'],
                    'Fiware-ServicePath': self.myconfig['Fiware-ServicePath']
                }

        except Exception as e:
            print('OrionSubscription', e)

    def get_subscription_usecase_list(self, service):
        result = None
        try:
            if self.usecase is not None:
                output = []

                start = 0
                limit = 20
                try_next = True
                headers = {
                    'Fiware-Service': service,
                    'Fiware-ServicePath': '/#'
                }
                while try_next:
                    url = f'{self.orion_server}/subscriptions?offset={start}&limit={limit}'
                    response = requests.get(url, headers=headers, timeout=self.api_timeout, verify=False)
                    if response.status_code == 200:
                        subsciption_list = response.json()
                        n = len(subsciption_list)
                        for sub_data in subsciption_list:
                            print('subscription data', sub_data)
                            if sub_data['description'].startswith(self.usecase):
                                output.append(sub_data)

                        if n == limit:
                            start += limit
                        else:
                            try_next = False
                    else:
                        print('get_subscription_usecase_list failed', response.status_code)
                        try_next = False

                result = output
            
        except Exception as e:
            print('get_subscription_usecase_list', e)
        return result

    def get_subscription_apiname_list(self):
        result = None
        try:
            output = []

            start = 0
            limit = 20
            try_next = True
            while try_next:
                url = f'{self.orion_server}/subscriptions?offset={start}&limit={limit}'
                response = requests.get(url, headers=self.get_headers, timeout=self.api_timeout, verify=False)
                if response.status_code == 200:
                    subsciption_list = response.json()
                    n = len(subsciption_list)
                    for sub_data in subsciption_list:
                        for entity in sub_data['subject']['entities']:
                            if entity['type'] == self.entity_type:
                                output.append(sub_data)
                    if n == limit:
                        start += limit
                    else:
                        try_next = False
                else:
                    print('get_subscription_apiname_list failed', response.status_code)
                    try_next = False

            result = output
            
        except Exception as e:
            print('get_subscription_apiname_list', e)
        return result

    def search_subscription(self):
        result = None
        try:
            start = 0
            limit = 20
            try_next = True
            while try_next:
                url = f'{self.orion_server}/subscriptions?offset={start}&limit={limit}'
                response = requests.get(url, headers=self.get_headers, timeout=self.api_timeout, verify=False)
                if response.status_code == 200:
                    subsciption_list = response.json()
                    n = len(subsciption_list)
                    for sub_data in subsciption_list:
                        if sub_data['description'] == self.subscription_key:
                            result = sub_data
                            try_next = False
                            break

                    if try_next:
                        if n == limit:
                            start += limit
                        else:
                            try_next = False
                else:
                    print('search_subscription failed', response.status_code)
                    try_next = False

        except Exception as e:
            print('search_subscription', e)
        return result

    def set_subscription(self, endpoint):
        result = False
        try:
            sub_data = self.search_subscription()
            if sub_data is None:
                print('new subscription')
                self.create_subscription(endpoint)
            else:
                print('update subscription')
                subscription_id = sub_data['id']
                self.update_subscription(endpoint, subscription_id)
            
        except Exception as e:
            print('set_subscription', e)
        return result

    def create_subscription(self, endpoint):
        result = False
        try:
            print('create_subscription called')
            url = f'{self.orion_server}/subscriptions'
            data = {
                'description': self.subscription_key,
                'subject': {
                    'entities': [
                        { 'idPattern': '.*', 'type': self.entity_type }
                    ],
                    'condition': {
                        'attrs': self.myconfig['subscription']['attrs']
                    }
                },
                'notification': {
                    'http': {
                        'url': endpoint
                    },
                    'attrsFormat': 'keyValues',
                    'throttling': 300       # 5分（300sec）に1回、サブスクリプションを発動する。
                }
            }
            print('subscription data', data)
            response = requests.post(url, json=data, headers=self.post_headers, timeout=self.api_timeout, verify=False)
            status_code = response.status_code
            if status_code == 201:
                # 作成OK
                payload = response.json()
                print('サブスクリプションを作成しました', payload)
                result = True
            else:
                print('サブスクリプションを作成できませんでした', status_code)

        except Exception as e:
            print('create_subscription', e)
        return result

    def update_subscription(self, endpoint, subscription_id):
        result = False
        try:
            url = f'{self.orion_server}/subscriptions/{subscription_id}'
            data = {
                'description': self.subscription_key,
                'subject': {
                    'entities': [
                        { 'idPattern': '.*', 'type': self.entity_type }
                    ],
                    'condition': {
                        'attrs': self.myconfig['subscription']['attrs']
                    }
                },
                'notification': {
                    'http': {
                        'url': endpoint
                    },
                    'attrsFormat': 'keyValues',
                    'throttling': 300       # 5分（300sec）に1回、サブスクリプションを発動する。
                }
            }
            response = requests.patch(url, json=data, headers=self.post_headers, timeout=self.api_timeout, verify=False)
            status_code = response.status_code
            if status_code == 204:
                # 更新OK
                payload = response.json()
                print('サブスクリプションを更新しました', payload)
                result = True
            else:
                print('サブスクリプションを更新できませんでした', status_code)
            
        except Exception as e:
            print('update_subscription', e)
        return result

    def delete_subscription(self, subscription_id):
        result = False
        try:
            url = f'{self.orion_server}/subscriptions/{subscription_id}'
            print('header', self.post_headers)
            response = requests.delete(url, headers=self.get_headers, timeout=self.api_timeout, verify=False)
            status_code = response.status_code
            if status_code == 204:
                # 作成OK
                print('サブスクリプションを削除しました')
                result = True
            else:
                print('サブスクリプションを削除できませんでした', status_code)
        
        except Exception as e:
            print('delete_subscription', e)
        return result


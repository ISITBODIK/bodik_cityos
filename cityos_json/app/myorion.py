import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

import requests
import json

import myes
from myconfig import MyConfig

from env import orion_server

class MyOrion:

    ua = 'BODIK/2.0'
    version = 'v2'
    api_timeout = 60
    list_separator = ';'

    def __init__(self):
        try:
            self.myconfig = None
            self.orion_server = orion_server
            self.filter_dict = {
                'wildcard': self.makeWildcardFilter,
                'term': self.makeTermFilter,
                'range': self.addFromToFilter,
                'list': self.addListFilter,
            }

        except Exception as e:
            print('Orion.init', e)
    
    def search(self, params):
        result = None
        try:
            obj = MyConfig()
            if 'apiname' in params:
                apiname = params['apiname']
                self.myconfig = obj.get_config(apiname)
            elif 'entity_type' in params:
                entity_type = params['entity_type']
                self.myconfig = obj.get_entity_config(entity_type)

            if self.myconfig is not None:
                self.entity_type = self.myconfig['entity_type']
                url = f'{orion_server}/{self.version}/op/query'
                print('url', url)
                offset = 0
                count = 100

                payload = self.make_query(params)
                print('payload', payload)

                output = []
                do_fetch = True
                while do_fetch:
                    headers = {
                        'User-Agent': self.ua,
                        'Content-Type': 'application/json',
                        'Fiware-Service': self.myconfig['Fiware-Service'],
                        'Fiware-ServicePath': self.myconfig['Fiware-ServicePath']
                    }
                    print('headers', headers)
                    q = {
                        'type': self.entity_type,
                        'options': 'keyValues',
                        'offset': offset,
                        'limit': count,
                    }
                    print('q', q)
                    response = requests.post(url, params=q, json=payload, headers=headers, timeout=self.api_timeout, verify=False)
                    status_code = response.status_code
                    print('status_code', status_code)
                    if status_code == 200:
                        data_list = response.json()
                        print('data_list', data_list)
                        n = len(data_list)
                        if n > 0:
                            output.extend(data_list)
                            if n == count:
                                offset += count
                            else:
                                do_fetch = False
                        else:
                            do_fetch = False
                    else:
                        print(response.text)
                        do_fetch = False

                    result = output

        except Exception as e:
            print('search', e)
        return result
    
    def make_query(self, params):
        result = None
        try:
            payload = {
                'entities': [
                    {
                        'idPattern': '.*',
                        'type': self.entity_type
                    }
                ],
                'attrs': [

                ],
            }
            q = self.build_query(params)
            if q != '':
                payload['expression'] = {
                    'q': q
                }

            result = payload

        except Exception as e:
            print('make_query', e)
        return result

    def build_query(self, params):
        result = None
        try:
            self.filter = []
            fields = self.myconfig['fields']
            for field in params:
                if field not in ['apiname', 'entity_type', 'lat', 'lon']:
                    value = params[field]
                    info = fields[field]
                    self.addFilter(field, value, info)

            if 'lat' in params and 'lon' in params and 'distance' in params:
                lat = params['lat']
                lon = params['lon']
                distance = params['distance']
                self.addDistanceFilter(lat, lon, distance)

            result = ';'.join(self.filter)

        except Exception as e:
            print('build_query', e)
        return result

    def makeWildcardFilter(self, key, value):
        try:
            if value:
                flt = f'{key}~={value}'
                self.filter.append(flt)

        except Exception as e:
            print('makeWildcardFilter', e)

    def makeTermFilter(self, key, value):
        try:
            if value:
                flt = f'{key}=={value}'
                self.filter.append(flt)

        except Exception as e:
            print('makeTermFilter', e)

    def makeRangeFilter(self, key, value1, value2):
        try:
            if value1 and value2:
                flt = f'{key}=={value1}..{value2}'
            else:
                if value1:
                    flt = f'{key}>={value1}'
                else:
                    flt = f'{key}<={value2}'

            self.filter.append(flt)

        except Exception as e:
            print('makeRangeFilter', e)

    def makeListFilter(self, key, value):
        try:
            if value:
                # for fiware
                value_text = ','.join(value)
                flt = f'{key}=={value_text}'
                self.filter.append(flt)

        except Exception as e:
            print('makeListFilter', e)


    def makeTextFilter(self, key, value):
        try:
            if value:
                flt = f'{key}==\'{value}\''
                self.filter.append(flt)

        except Exception as e:
            print('makeTextFilter', e)

    def addIntegerFilter(self, key, value):
        try:
            if value:
                if type(value) == str:
                    if self.list_separator in value:
                        token = value.split(self.list_separator)
                        if len(token) == 2:
                            from_value = int(token[0])
                            to_value = int(token[1])
                            self.makeRangeFilter(key, from_value, to_value)
                        else:
                            print('addIntegerFilter: invalid parameter', key, value)
                    else:
                        self.makeTermFilter(key, value)
                elif type(value) == dict:
                    from_value = value['from']
                    to_value = value['to']
                    self.makeRangeFilter(key, from_value, to_value)

        except Exception as e:
            print('addWildcardFilter', e)

    def addFloatFilter(self, key, value):
        try:
            if value:
                if type(value) is str:
                    if self.list_separator in value:
                        token = value.split(self.list_separator)
                        if len(token) == 2:
                            from_value = float(token[0])
                            to_value = float(token[1])
                            self.makeRangeFilter(key, from_value, to_value)
                    else:
                        self.makeTermFilter(key, value)

                elif type(value) is dict:
                    from_value = value['from']
                    to_value = value['to']
                    self.makeRangeFilter(key, from_value, to_value)

        except Exception as e:
            print('addFloatFilter', e)

    def addFromToFilter(self, key, value):
        try:
            if value:
                if type(value) is str:
                    if self.list_separator in value:
                        token = value.split(self.list_separator)
                        if len(token) == 2:
                            self.makeRangeFilter(key, token[0], token[1])
                    else:
                        self.makeTermFilter(key, value)

                elif type(value) is dict:
                    from_value = value['from']
                    to_value = value['to']
                    self.makeRangeFilter(key, from_value, to_value)

        except Exception as e:
            print('addFromToFilter', e)

    def addListFilter(self, key, value):
        try:
            if value:
                if type(value) is str:
                    array = None
                    if self.list_separator in value:
                        array = value.split(self.list_separator)
                    else:
                        array = []
                        array.append(value)
                    self.makeListFilter(key, array)

                elif type(value) is list:
                    self.makeListFilter(key, value)

        except Exception as e:
            print('addListFilter', e)

    def addFilter(self, field, value, info):
        result = False
        try:
            print('info', info)
            field_type = info['field_type']
            filter_type = info['filter']
            if field_type in 'Integer':
                self.addIntegerFilter(field, value)
            elif field_type in 'Float':
                self.addFloatFilter(field, value)
            else:
                if filter_type in self.filter_dict:
                    self.filter_dict[filter_type](field, value)
                else:
                    self.makeWildcardFilter(field, value)

        except Exception as e:
            print('addFilter', e)
        return result
    
    def addDistanceFilter(self, lat, lon, distance):
        try:
            self.qLocation = {}
            if lat and lon and distance:
                print('addDistanceFilter')
                # for fiware
                self.qLocation['georel'] = f'near;maxDistance:{distance}'
                self.qLocation['geometry'] = 'point'
                self.qLocation['coords'] = f'{lat},{lon}'
                self.qLocation['orderBy'] = f'geo:distance'

        except Exception as e:
            print('addDistanceFilter', e)        

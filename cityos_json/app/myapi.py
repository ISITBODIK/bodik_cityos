import json

from myconfig import MyConfig
from configFile import configFile
import myes

class MyAPI(configFile):

    def __init__(self):
        try:
            self.config_type = None
            self.organ_code = None
            self.prefix = None

        except Exception as e:
            print('MyAPI.init', e)
    
    def make_config(self, config):
        result = None
        try:
            print('make_config', config)
            apiname = config['apiname']
            if self.prefix is not None and not apiname.startswith(self.prefix):
                apiname = f'{self.prefix}{apiname}'
            config['apiname'] = apiname
            #config['index'] = apiname
            #config['display_name'] = apiname

            myconfig = self.update_myconfig(config)
            if myconfig is not None:
                print('myconfig', myconfig)
                result = apiname

        except Exception as e:
            print('make_config', e)
        return result

    def make_es_index(self, apiname):
        result = False
        try:
            obj = MyConfig()
            myconfig = obj.get_config(apiname)
            result = myes.create_index(myconfig)
        except Exception as e:
            print('make_es_index', e)
        return result
    
    def delete_es_index(self, apiname):
        result = False
        try:
            obj = MyConfig()
            myconfig = obj.get_config(apiname)
            result = myes.delete_index(myconfig)
        except Exception as e:
            print('delete_es_index', e)
        return result
    
    def search_es_data(self, apiname):
        result = False
        try:
            obj = MyConfig()
            myconfig = obj.get_config(apiname)
            qs = {
                'query': {
                    'match_all': {}
                }
            }
            print('search', myconfig['index'])
            result = myes.search_document(myconfig, qs)
        except Exception as e:
            print('search_es_data', e)
        return result


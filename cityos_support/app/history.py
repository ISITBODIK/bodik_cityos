import myes
from myconfig import MyConfig

class History:

    def __init__(self, apiname):
        try:
            self.apiname = apiname
            obj = MyConfig()
            self.myconfig = obj.get_config(apiname)
        except Exception as e:
            print('History.init', e)
    
    def get_data(self):
        result = None
        try:
            qs = {
                'query': {
                    'match_all': {}
                }
            }
            result = myes.search_document(self.myconfig, qs)

        except Exception as e:
            print('get_data', e)
        return result
    
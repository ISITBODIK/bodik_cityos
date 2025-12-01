from myapi import MyAPI

class DpAPI(MyAPI):

    def __init__(self):
        try:
            self.config_type = self.TYPE_DPAPI
            self.dataset_level = 'L1'
            self.organ_code = None
            self.prefix = None
            
        except Exception as e:
            print('DPApi.__init__', e)


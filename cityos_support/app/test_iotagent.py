import requests
import json

from env import iotagent_server, iotagent_provision_server, orion_server

class TestIotAgent:

    orion_version = 'v2'
    entity_type = "temperature"
    ua = 'BODIK/2.0'
    fiware_service = 'bodik'
    fiware_service_path = '/bodik'
    api_timeout = 10
    apikey = ''
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

    def set_service_group_provisioning(self):
        result = False
        try:
            url = f'{iotagent_provision_server}/iot/services'
            params = {
                'services': [
                    {
                        'apikey': self.apikey,
                        'cbroker': orion_server,
                        'entity_type': self.entity_type,
                        'resource': '/iot/json'
                    }
                ]
            }

            r = requests.post(url, json=params, headers=self.post_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 201:    # 新規作成成功
                result = True
            elif r.status_code == 204:  # 更新成功
                result = True
            else:
                print('status_code', r.status_code)

        except Exception as e:
            print('set_data', e)
        return result

    def set_device_provisioning(self):
        result = False
        try:
            url = f'{iotagent_provision_server}/iot/devices'
            params = {
                'devices': [
                    {
                        'device_id': 'hirano',
                        'cbroker': orion_server,
                        'entity_type': self.entity_type,
                        'resource': '/iot/json'
                    }
                ]
            }

            r = requests.post(url, json=params, headers=self.post_headers, timeout=self.api_timeout, verify=False)
            if r.status_code == 201:    # 新規作成成功
                result = True
            elif r.status_code == 204:  # 更新成功
                result = True
            else:
                print('status_code', r.status_code)

        except Exception as e:
            print('set_data', e)
        return result


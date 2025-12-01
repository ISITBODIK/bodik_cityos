from fastapi import FastAPI, HTTPException, Depends

import os
import requests

KEYCLOAK_REALM_URL = os.getenv("KEYCLOAK_REALM_URL")

KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_REALM_URL}/protocol/openid-connect/token"
KONG_CLIENT = os.getenv('KONG_CLIENT')
KONG_SECRET = os.getenv('KONG_SECRET')

demo_user = os.getenv('demo_user_name')
demo_pass = os.getenv('demo_user_pass')

photo_user = os.getenv('photo_user_name')
photo_pass = os.getenv('photo_user_pass')

class myKeycloak:

    def __init__(self):
        pass
    
    def login_orion(self, param):
        result = None
        try:
            data = {
                'grant_type': 'password',
                'client_id': KONG_CLIENT,
                'client_secret': KONG_SECRET,
                'username': param['username'],
                'password': param['password']
            }
            print('data', data)
            response = requests.post(KEYCLOAK_TOKEN_URL, data=data, verify=False)
            if response.status_code == 200:
                result = response.json()
            else:
                raise HTTPException(status_code=401, detail="invalid credentials")
            
        except Exception as e:
            print('login_orion', e)
        return result

    def refresh_orion(self, param):
        result = None
        try:
            data = {
                'grant_type': 'refresh_token',
                'client_id': KONG_CLIENT,
                'client_secret': KONG_SECRET,
                'refresh_token': param['refresh_token']
            }
            response = requests.post(KEYCLOAK_TOKEN_URL, data=data, verify=False)
            if response.status_code == 200:
                result = response.json()
            else:
                raise HTTPException(status_code=401, detail="invalid refresh token")
            
        except Exception as e:
            print('refresh_orion', e)
        return result

    def login_orion_demo(self, apiname):
        result = None
        try:
            data = None
            if apiname == 'photo':
                data = {
                    'grant_type': 'password',
                    'client_id': KONG_CLIENT,
                    'client_secret': KONG_SECRET,
                    'username': photo_user,
                    'password': photo_pass
                }
            else:
                data = {
                    'grant_type': 'password',
                    'client_id': KONG_CLIENT,
                    'client_secret': KONG_SECRET,
                    'username': demo_user,
                    'password': demo_pass
                }

            response = requests.post(KEYCLOAK_TOKEN_URL, data=data, verify=False)
            if response.status_code == 200:
                result = response.json()
                print('login_orion_demo', result)
            else:
                raise HTTPException(status_code=401, detail="invalid credentials")
            
        except Exception as e:
            print('login_orion_demo', e)
        return result


import requests
import json
from typing import Optional
import os
from jose import jwt, jwk
from dotenv import load_dotenv

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

from exceptions import UnauthorizedError, ForbiddenError, ServiceUnavailableError, AuthError

# .envファイルをロード
load_dotenv()

HOSTNAME = os.getenv("KC_HOSTNAME")
KEYCLOAK_REALM_URL = os.getenv("KEYCLOAK_REALM_URL")

AUTH_METHOD = os.getenv("AUTH_METHOD", "POST").upper()
ACL_METHOD = os.getenv("ACL_METHOD", "POST").upper()

EMQX_CLIENT = os.getenv('EMQX_CLIENT')
EMQX_SECRET = os.getenv('EMQX_SECRET')

KONG_CLIENT = os.getenv('KONG_CLIENT')
KONG_SECRET = os.getenv('KONG_SECRET')

client_list = {
    'MQTT-broker': {
        'client_id': EMQX_CLIENT,
        'client_secret': EMQX_SECRET
    },
    'kong': {
        'client_id': KONG_CLIENT,
        'client_secret': KONG_SECRET
    }
}

# KeycloakのJWKS (JSON Web Key Set) URL
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_REALM_URL}/protocol/openid-connect/certs"
#KEYCLOAK_JWKS_URL = f"https://keycloak:8443/realms/cityos/protocol/openid-connect/certs"
# Keycloakのトークンエンドポイント
KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_REALM_URL}/protocol/openid-connect/token"
#KEYCLOAK_TOKEN_URL = f"https://keycloak:8443/realms/cityos/protocol/openid-connect/token"

KEYCLOAK_ISSUER = f'https://{HOSTNAME}:8443/realms/cityos' # JWTの 'iss' と一致させる

_acl_cache = {}

class myKeycloak:

    def __init__(self):
        #self.keycloak_server = keycloak_server
        print('KEYCLOAK_REALM_URL', KEYCLOAK_REALM_URL)
        pass

    # emqxのカスタムプラグインから呼び出される
    def mqtt_auth(self, clientid, username, password):
        result = None
        try:
            user_info = self.verify_keycloak_credentials('MQTT-broker', username, password)
            if user_info is not None:
                print('user_info', user_info)
                
                mqtt_topics = user_info['mqtt_topics']
                groups = user_info['groups']

                # ACL用にキャッシュに保存
                _acl_cache[username] = {
                    "mqtt_topics": mqtt_topics,
                    "groups": groups
                }

                # status_code=200を返せばOK。JSONの中身は見ていない。
                result = {
                    'status': 'OK',
                    'metadata': {
                        'mqtt_topics': mqtt_topics,
                        'groups': groups
                    }
                }
                print('result', result)
            else:
                raise UnauthorizedError('Invalid username or password')

        except AuthError:
            raise

        except Exception as e:
            print('mqtt_auth', e)
            raise AuthError('Invalid username or password')
        
        return result

    def mqtt_acl(self, access, clientid, username, topic):
        result = None
        try:
            acl_ok = False
            acl_info = _acl_cache.get(username)
            if acl_info is not None:
                allowed_topics = acl_info.get("mqtt_topics", [])
                if '#' in allowed_topics:
                    # 管理者
                    acl_ok = True
                else:
                    if topic in allowed_topics:
                        # 完全一致
                        acl_ok = True
                    else:
                        # ワイルドカード対応
                        for t in allowed_topics:
                            if t.endswith('/#') and topic.startswith(t[:-2]):
                                acl_ok = True

                if acl_ok: 
                    result = {
                        'result': 'allow'
                    }
                else:
                    print('ACL error', topic)
                    result = {
                        'result': 'deny'
                    }

        except Exception as e:
            print('mqtt_acl', e)
            result = {
                'result': 'deny'
            }

        return result

    def kong_auth(self, username, password):
        result = None
        try:
            user_info = self.verify_keycloak_credentials('kong', username, password)
            if user_info is not None:
                print('user_info', user_info)
                
                allowed_fiware_scopes = user_info['allowed_fiware_scopes']
                groups = user_info['groups']
                result = {
                    'status': 'OK',
                    'metadata': {
                        'allowed_fiware_scopes': allowed_fiware_scopes,
                        'groups': groups
                    }
                }
                print('result', result)
            else:
                raise UnauthorizedError('Invalid username or password')

        except AuthError:
            raise

        except Exception as e:
            print('kong_auth', e)
            raise AuthError('Invalid username or password')
        
        return result

    def get_jwks(self):
        result = None
        try:
            try:
                response = requests.get(KEYCLOAK_JWKS_URL, timeout=5, verify=False)
                #response = requests.get(KEYCLOAK_JWKS_URL, timeout=5, verify='./ssl/bodik.jp.pem')
                response.raise_for_status()
                jwks = response.json()
                result = jwks
                print('jwks', jwks)
                print(f"Successfully fetched JWKS from {KEYCLOAK_JWKS_URL}")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching JWKS from Keycloak: {e}")

        except Exception as e:
            print('get_jwks', e)

        return result

    def verify_keycloak_credentials(self, clientid: str, username: str, password: str) -> Optional[dict]:
        try:
            """
            KeycloakのDirect Access Grants (パスワードグラント) を使用して認証を試みる。
            成功すればユーザー情報（クレーム）を返す。
            """
            myjwt = self.get_jwt(clientid, username, password)
            if myjwt is not None:
                # JWTトークンを検証
                jwks = self.get_jwks()
                if jwks is not None:
                    decoded_token = jwt.decode(
                        myjwt,
                        jwks, # **** ここにJWKSオブジェクト全体を渡す ****
                        algorithms=["RS256"], # Keycloakのデフォルトアルゴリズム
                        #audience=clientid, # クライアントIDをaudienceとして検証
                        audience='account', # クライアントIDをaudienceとして検証
                        issuer=KEYCLOAK_ISSUER, # JWTの 'iss' と一致させる
                        options={
                            "require_exp": True,      # 有効期限の検証を必須にする
                            "verify_signature": True, # 署名検証を必須にする
                            "verify_at_hash": False   # at_hashの検証は必須ではない場合も
                        }
                    )
                    print("JWT token successfully decoded and verified!", decoded_token)
                    result = decoded_token # 認証成功、デコードされたトークンを返す
                else:
                    print("Failed to retrieve JWKS.")
            else:
                raise AuthError('Invalid clientid')

        except requests.exceptions.RequestException as e:
            print(f"Keycloak authentication request failed: {e}")
            raise ServiceUnavailableError('Could not connect to Keycloak for authentication')
        except Exception as e:
            print(f"Error during JWT verification: {e}")
            raise ServiceUnavailableError('Internal error during Keycloak token processing')
        return result

    def get_jwt(self, clientid, username, password):
        result = None
        try:
            if clientid in client_list:
                client_info = client_list[clientid]

                result = None
                data = {
                    "grant_type": "password",
                    "client_id": client_info['client_id'],
                    "client_secret": client_info['client_secret'],
                    "username": username,
                    "password": password,
                    #"scope": "openid" # 必要に応じてscopeを追加
                }
                print('data', data)
                print('url', KEYCLOAK_TOKEN_URL)
                response = requests.post(KEYCLOAK_TOKEN_URL, data=data, timeout=10, verify=False)
                print('status_code', response.status_code)
                response.raise_for_status() # HTTPエラーが発生した場合に例外を投げる
                token_response = response.json()
                print('token', token_response)
                myjwt = token_response.get("access_token")
                result = myjwt
            else:
                print('unknown clientid', clientid)
                
        except requests.exceptions.RequestException as e:
            print(f"Keycloak authentication request failed: {e}")
            raise ServiceUnavailableError('Could not connect to Keycloak for authentication')

        except Exception as e:
            print(f"Error during JWT verification: {e}")
            raise ServiceUnavailableError('Internal error during Keycloak token processing')
       
        return result


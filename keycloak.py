import requests
import json
import urllib3

# SSL警告を無効にする（自己署名証明書などを使用している場合のみ。本番環境では非推奨）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://test.bodik.jp:8443/realms/cityos/protocol/openid-connect/token'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
payload = {
    'grant_type': "password",
    'client_id': '',
    'client_secret': '',
    'username': '',
    'password': ''
}

r = requests.post(url, headers=headers, data=payload, verify=False)
if r.status_code == 200:
    print('認証確認')
    print(json.dumps(r.json(), indent=2))
else:
    print('認証失敗', r.status_code)

import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# JWKSから取得した 'n' と 'e' の値をここに貼り付けてください
kid = ""
n_b64 = ""
e_b64 = ""

# Base64URLデコード
n_int = int.from_bytes(base64.urlsafe_b64decode(n_b64 + '=='), 'big')
e_int = int.from_bytes(base64.urlsafe_b64decode(e_b64 + '=='), 'big')
print('n-int', n_int)
print('e-int', e_int)

# 公開鍵オブジェクトを生成
public_numbers = rsa.RSAPublicNumbers(e_int, n_int)
public_key = public_numbers.public_key(default_backend())
print('public_key', public_key)

# PEM形式にシリアライズ
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Kong Managerに貼り付けるための文字列を生成
rsa_public_key_string = pem.decode('utf-8').replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '').replace('\n', '')

print(f"Key ID (kid): {kid}")
print("-" * 50)
print("RSA Public Key for Kong Manager:")
print(rsa_public_key_string)

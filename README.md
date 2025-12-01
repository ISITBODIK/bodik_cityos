# SSL証明書のセットアップ

SSL証明書はそれぞれの環境に合わせて用意する。  
ここでは、次のようなファイルであることを前提に、SSL証明書のセットアップを説明する。  

    cityos.key
    cityos.pem

## SSL証明書を ./ssl に配置する。

例

    ./ssl/cityos.key
    ./ssl/cityos.pem

## ./envフォルダに、Kong用とkeycloak用の環境設定ファイルを置く。

./env/kong-ssl.env

    KONG_CLUSTER_CERT=/usr/local/kong/cert/cityos.pem
    KONG_CLUSTER_CERT_KEY=/usr/local/kong/cert/cityos.key
    KONG_SSL_CERT=/usr/local/kong/cert/cityos.pem
    KONG_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key
    KONG_ADMIN_SSL_CERT=/usr/local/kong/cert/cityos.pem
    KONG_ADMIN_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key
    KONG_ADMIN_GUI_SSL_CERT=/usr/local/kong/cert/cityos.pem
    KONG_ADMIN_GUI_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key


./env/keycloak-ssl.env

    KC_HTTPS_CERTIFICATE_FILE=/etc/ssl/cityos/cityos.pem
    KC_HTTPS_CERTIFICATE_KEY_FILE=/etc/ssl/cityos/cityos.key

## これらのファイルは、docker-compose.yml から参照される

kong

    volumes:
      - ./ssl:/usr/local/kong/cert
    env_file:
      - ./env/kong-ssl.env

keycloak

    volumes:
      - ./ssl:/etc/ssl/cityos
    env_file:
      - ./env/keycloak-ssl.env

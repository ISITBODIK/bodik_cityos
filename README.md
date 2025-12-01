1. SSL証明書を ./ssl に配置する。<br>
    例

    cityos.key
    cityos.pem

./envフォルダに、Kong用とkeycloak用の環境設定ファイルを置く。<br>
    kong.ssl.env

    KONG_CLUSTER_CERT=/usr/local/kong/cert/cityos.pem
    KONG_CLUSTER_CERT_KEY=/usr/local/kong/cert/cityos.key
    KONG_SSL_CERT=/usr/local/kong/cert/cityos.pem
    KONG_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key
    KONG_ADMIN_SSL_CERT=/usr/local/kong/cert/cityos.pem
    KONG_ADMIN_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key
    KONG_ADMIN_GUI_SSL_CERT=/usr/local/kong/cert/cityos.pem
    KONG_ADMIN_GUI_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key

    keycloak-ssl.env

    KC_HTTPS_CERTIFICATE_FILE=/etc/ssl/cityos/cityos.pem
    KC_HTTPS_CERTIFICATE_KEY_FILE=/etc/ssl/cityos/cityos.key

※これらのファイルは、docker-compose.yml から参照されている<br>

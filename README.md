1. SSL証明書を ./ssl に配置する。<br>
   例<br>
      cityos.key<br>
      cityos.pem<br>
<br>
2. ./envフォルダに、Kong用とkeycloak用の環境設定ファイルを置く。<br>
   kong.ssl.env<br>
      KONG_CLUSTER_CERT=/usr/local/kong/cert/cityos.pem<br>
      KONG_CLUSTER_CERT_KEY=/usr/local/kong/cert/cityos.key<br>
      KONG_SSL_CERT=/usr/local/kong/cert/cityos.pem<br>
      KONG_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key<br>
      KONG_ADMIN_SSL_CERT=/usr/local/kong/cert/cityos.pem<br>
      KONG_ADMIN_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key<br>
      KONG_ADMIN_GUI_SSL_CERT=/usr/local/kong/cert/cityos.pem<br>
      KONG_ADMIN_GUI_SSL_CERT_KEY=/usr/local/kong/cert/cityos.key<br>
<br>
   keycloak-ssl.env<br>
      KC_HTTPS_CERTIFICATE_FILE=/etc/ssl/cityos/cityos.pem<br>
      KC_HTTPS_CERTIFICATE_KEY_FILE=/etc/ssl/cityos/cityos.key<br>
<br>
   ※これらのファイルは、docker-compose.yml から参照されている<br>

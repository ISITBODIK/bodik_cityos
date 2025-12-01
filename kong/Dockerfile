FROM kong:3.9

# openssl/luaossl のインストールは不要

# カスタムプラグインをコピーする (所有権は kong:kong のまま)
COPY --chown=kong:kong ./plugins/fiware-authz/ /usr/local/share/lua/5.1/kong/plugins/fiware-authz/
COPY --chown=kong:kong ./plugins/fiware-public/ /usr/local/share/lua/5.1/kong/plugins/fiware-public/
COPY --chown=kong:kong ./plugins/check-scope/ /usr/local/share/lua/5.1/kong/plugins/check-scope/

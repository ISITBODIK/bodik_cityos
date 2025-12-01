# keycloak_admin_client.py
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
import os

class KeycloakAdminClient:
    def __init__(self):
        self.keycloak_connection = KeycloakOpenIDConnection(
            server_url=os.getenv("KEYCLOAK_SERVER_URL"),
            realm_name=os.getenv("KEYCLOAK_REALM"),
            client_id=os.getenv("KEYCLOAK_ADMIN_CLIENT_ID"), # e.g., admin-cli
            client_secret_key=os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET", None), # サービスアカウントの場合
            user_realm_name="master" # master レルムの admin ユーザーで認証する場合
        )
        self.keycloak_admin = KeycloakAdmin(
            connection=self.keycloak_connection,
            # パスワードグラントで認証する場合
            user_realm_name="master",
            username=os.getenv("KEYCLOAK_ADMIN_USERNAME"),
            password=os.getenv("KEYCLOAK_ADMIN_PASSWORD")
        )
        # トークン取得
        self.keycloak_admin.connection.set_token(
            self.keycloak_admin.connection.get_token()
        )

    def get_all_users(self):
        return self.keycloak_admin.get_users()

    def create_user(self, user_data):
        return self.keycloak_admin.create_user(user_data)

    def update_user(self, user_id, user_data):
        return self.keycloak_admin.update_user(user_id, user_data)

    def delete_user(self, user_id):
        return self.keycloak_admin.delete_user(user_id)

    def get_user_by_username(self, username):
        users = self.keycloak_admin.get_users({"username": username})
        return users[0] if users else None

# 環境変数を設定 (例: .env ファイルなど)
# KEYCLOAK_SERVER_URL=https://your-keycloak-host:8443
# KEYCLOAK_REALM=your-realm
# KEYCLOAK_ADMIN_USERNAME=admin
# KEYCLOAK_ADMIN_PASSWORD=your_admin_password
# KEYCLOAK_ADMIN_CLIENT_ID=admin-cli # または作成したサービスアカウントのクライアントID
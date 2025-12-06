# Kong セットアップ
KongをAPIゲートウェイとして利用する。  

詳細は、「Kong構築資料」を参照。

## サービス

|サービス|サーバー|
|----|----|
|orion-service|http://orion:1026|
|webapp-service|http://cityos_json:8080|
|tile-service|http://tileserver|

## ルート

|ルート|パス|プロトコル|用途|サービス|プラグイン|
|----|----|----|----|----|----|
|orion-route|/v2|https|Orionアクセス|orion-service|fiware-authz|
|webapp-route|/webapp|https|Webアプリを提供|webapp-service||
|auth-route|/auth|https|認証支援|webapp-service||
|myapi-route|/myapi|https|MyAPI情報|webapp-service||
|uploads-route|/uploads|https|ファイルアップロード|webapp-service|fiware-authz|
|download-route|/download|https|ファイルダウンロード|webapp-service||
|tile-route|/tile|https|タイルサーバー|tile-service|check-scope|

## カスタムプラグイン

|カスタムプラグイン|用途|
|----|----|
|fiware-authz|指定されたアクセストークンとFiware-Servce,Fiware-ServicePathの組み合わせの整合性をチェックする。|


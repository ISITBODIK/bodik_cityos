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

|ルート|パス|用途|サービス|プラグイン|
|----|----|----|----|----|
|orion-route|/v2|Orionアクセス|orion-service|fiware-authz|
|webapp-route|/webapp|Webアプリを提供|webapp-service||
|auth-route|/auth|認証支援|webapp-service||
|myapi-route|/myapi|MyAPI情報|webapp-service||
|uploads-route|/uploads|ファイルアップロード|webapp-service|fiware-authz|
|download-route|/download|ファイルダウンロード|webapp-service||
|tile-route|/tile|タイルサーバー|tile-service|check-scope|

## カスタムプラグイン

|カスタムプラグイン|用途|
|----|----|
|fiware-authz|指定されたアクセストークンとFiware-Servce,Fiware-ServicePathの組み合わせの整合性をチェックする。|

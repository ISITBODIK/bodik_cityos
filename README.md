# BODIK CityOS セットアップ手順
BODIK CityOSのソースコードをgithubから取り込み、システムを動かすために必要な作業を記載する。
		
## (1) 事前準備
githubからBODIK CityOSリポジトリをクローンする前に、サーバーに必要なモジュールを導入しておく。  
BODIK CityOSを動かすためには、次のようなモジュールを必要とする。
		
	git
	docker, docker compose
	python（3.12〜）
	unzip
		
[almalinux.sh](almalinux.sh) を参照。
		
## (2) BODIK CityOSリポジトリからクローンする
下記コマンドでソースコードをクローンする。  
クローンしたら、setup_dev.sh を実行する。

	git clone https://github.com/isitbodik/bodik_cityos.git .
	./setup_dev.sh


## (3) SSL証明書をセットする
HTTPS通信のためのSSL証明書は、環境ごとに用意すること。  
設定手順は、[SETUP_SSL.md](SETUP_SSL.md) を参照。	

## (4) 環境設定ファイルをコピーする
「copy_env.sh」を使って、環境設定ファイル（env.py, env.js）を作成する。

	./copy_env.sh cityos_support
	./copy_env.sh cityos_json
	./copy_env.sh cityos_subsc
	./copy_env.sh cityos_mqttsubsc

上記コマンドで環境設定ファイル（env.py, env.js）を初期設定する。  
必要に応じて上記ファイルを編集する必要がある。

## (5) .envファイルを作成する
環境ごとのセキュアな情報は、.envファイルに記述する。

	cp env.txt .env

※.envファイルには必要に応じて情報を追加する。  

## (6) docker compose を使ってシステムを起動する

	docker compose up -d --build

## (7) keycloakセットアップ（準備中）
ユーザー登録など、ユーザー認証に関する設定を行う。  
keycloakの管理画面を表示する。

	https://<cityosのURL>:8086

詳細は、[SETUP_KEYCLOAK.md](SETUP_KEYCLOAK.md) を参照。

## (8) Kongセットアップ（準備中）
APIゲートウェイはKongを使用する。  
Kongの管理画面を表示する。

	https://<cityosのURL>:8088

詳細は、[SETUP_KONG.md](SETUP_KONG.md) を参照。

## (9) MyAPI登録（準備中）
BODIK CityOSにデータを取り込むには、事前に「データセット定義JSON」を作成し、CityOSに登録する必要がある。（MyAPI登録作業）  
詳細は、[SETUP_MYAPI.md](SETUP_MYAPI.md) を参照。

## (10) データ取り込み（準備中）
外部からBODIK CityOSにデータを取り込むには、「BODIK ODGWR」を利用する。

## (11) タイルサーバーセットアップ（準備中）
地理空間サーバーとしてタイルサーバーを提供する。


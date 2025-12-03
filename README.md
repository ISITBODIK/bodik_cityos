# BODIK CityOS セットアップ手順

BODIK CityOSのソースコードをgithubから取り込み、システムを動かすために必要な作業を記載します。		
		
## 1 事前準備
	githubからBODIK CityOSリポジトリをクローンする前に、サーバーに必要なモジュールを導入しておく  
	BODIK CityOSに必要なモジュールは	
		
		git
		docker, docker compose
		python（3.12〜）
		unzip
		
	BODIK CityOSリポジトリの「almalinux.sh」を参考にしてください。	
		
		
## 2 BODIK CityOSリポジトリをクローンする
		
		git clone https://github.com/isitbodik/bodik_cityos.git .
		
		
## 3 SSL証明書をセットする
		
	BODIK CityOSリポジトリの「SETUP_SSL.md」を参考にしてください。	
		
		
## 4 		
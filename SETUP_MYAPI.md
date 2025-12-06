# MyAPIの仕組み
CityOSでは、Fiwareで扱うデータセットを「MyAPI」と呼ぶ仕組みで管理する。  
MyAPIは、データセットのデータモデル、特徴などを「データセット構成JSONファイル」に記述し、CityOSに登録する仕組みである。  
CityOSに何らかのデータを登録する場合、次の手順で操作する。  

## ０．事前準備

### (1) データセット構成JSONファイルを作成する
データセット構成JSONファイルには次の情報を含む。

    Orionに登録する「Fiware-Service」「Fiware-ServicePath」「entity_type」
    データモデル情報（データ型、英語属性名など）
    Orionのユニークキー情報
    履歴DBのユニークキー情報
    サブスクリプションに必要な情報

データセット構成JSONファイルの詳細は、仕様書を確認する。  

## １．BODIK CityOSでの作業

### (2) データセット構成JSONファイルをCityOSに登録する
CityOS管理者が「cityos_support」コンテナを使って登録する。  

### (3) 新しく登録するデータセットのデータをODGWRから書き込めるようにする
CityOS管理者がCityOSのKeycloakを使って、ODGWRのデータ登録用ユーザーに対して、新しいデータセットの書き込み許可を設定する。  

## ２．BODIK ODGWRでの作業

### (4) データセット構成JSONファイルをODGWRに登録する
CityOS管理者が「odgwr_support」コンテナを使って登録する。  

### (5) ODGWRに個別インポータを登録する
新しいデータセットを登録するインポータを開発し、ODGWRで動かす。  
CityOSへのデータ登録は、ODGWRのサポート機能を提供するので利用する。  
問題なければ、ODGWRのcrontabを使って自動実行させる。  

## ３．BODIK CityOSでの作業

### (6) 履歴DBに蓄積する場合は、サブスクリプションを登録する
CityOS管理者が「cityos_subsc」コンテナを使って登録する。  

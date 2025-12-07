# MyAPI仕様書
データセット構成JSONファイルに記載する情報を説明する。

## データセット構成JSONファイルの項目

### 必須項目
|項目|型|説明|
|----|----|----|
|apiname|文字列|MyAPIの名前|
|display_name|文字列|MyAPIの表示名|
|index|文字列|履歴DB（elasticsearch）のインデックス|
|entity_type|文字列|ngsiのエンティティ名|
|Fiware-Service|文字列|FIWAREのサービス名|
|Fiware-ServicePath|文字列|FIWAREのサービスパス|
|geometry|文字列|地理情報の型　('', 'Point')|
|geometry_field|文字列|地理情報の英語項目名|
|key|辞書|DBのレコードを特定する属性名の配列。<br>Orion（fiware）と履歴DB（history）、それぞれを指定する。|
|subscription|辞書|サブスクリプション時、レコードの更新を検知する属性名|
|dataModel|辞書|データモデル。項目名、英語項目名、データ型を辞書形式で列挙する。|

### CKAN項目
CKANからデータを取り込む場合、情報を追加する必要がある。  

|項目|型|説明|
|----|----|----|
|tag_only|文字列|'TRUE'の場合、必要なタグがセットされたデータセットを検索する。|
|tag_list|文字列|タグの配列|
|select_latest|文字列|'TRUE'の場合、複数のリソースファイルが見つかった場合、更新時刻が最新のものを採用する。|
|dataset_title_list|文字列|データセット名に指定した文字列を含むデータセットを検索する。|
|resource_title|文字列|リソース名に指定した文字列を含むリソースを検索する。|
|resource_filename|文字列|リソースのファイル名に指定した文字列を含むリソースを検索する。|
|format_list|文字列|リソースのフォーマット。通常は'csv'を指定する。|
|must_fields|文字列の配列|必須の項目名の配列。|

BODIK ODGWRは、「tag_only」項目が存在するMyAPIに対して、CKAN項目で指定された情報を使ってBODIK ODCSから対象となるデータを探し、BODIK CityOSにデータを取り込む。  

## 項目別説明

### key項目
Orion(fiware)と履歴DB(history)にレコードを登録するときにキー情報を構成する項目を列挙する。  
Orionは、ある事象のリアルタイムデータを記録するので、基本的に時刻情報をキーに含まない。  
履歴データは、時間の変化に応じてレコードが追加されるので、時刻情報をキーに含む。  

履歴データを蓄積しない場合、'key'項目に'fiware'を指定しない。  
リアルタイムデータではなく、統計データとして扱い場合は、'key'項目に'history'を指定しない。

    'key': {
      'fiware': {
        'fields': [ <英語項目名>, <英語項目名> ]
      },
      'history': {
        'fields': [ <英語項目名>, <英語項目名>, <英語項目名> ]
      }
    }
    
### subsctiption項目

    'subscription': {
      'attrs': [ <英語項目名>, <英語項目名> ]
    }
    
### dataModel項目

    'dataModel': {
      <項目名>: {
        'field_name': <英語項目名>,
        'type': <データ型>
      },

#### データ型

|項目|説明|
|----|----|
|Keyword|文字列（完全一致検索）|
|String|文字列（部分一致検索）|
|Integer|整数|
|Float|浮動小数点|
|Point|位置情報|

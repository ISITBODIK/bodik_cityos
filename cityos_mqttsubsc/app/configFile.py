# 事前定義
import json

from myconfig import MyConfig

class configFile:

    # dataset_type
    TYPE_MSDS = 'msds'              # msds      自治体標準ODS
    TYPE_MYAPI = 'myapi'            # myapi     独自APIの基底クラスID
    TYPE_CMAPI = 'cmapi'            # cmapi     全国共通API
    TYPE_LGAPI = 'lgapi'            # lgapi     自治体のMyAPI
    TYPE_DPAPI = 'dpapi'            # dpapi     データ基盤のMyAPI

    config = {}

    def __init__(self):
        try:
            self.config_type = None
            self.dataset_level = None
            self.organ_code = None
            self.prefix = None

        except Exception as e:
            print("ERROR configFile.init", e)

    def update_myconfig(self, config):
        result = None
        try:
            print('update_myconfig called')
            objConfig = MyConfig()

            myconfig = self.reshape(self.prefix, config)
            if myconfig is not None:
                apiname = myconfig["apiname"]
                # 既存の定義を取得
                myconfig_prev = objConfig.get_config(apiname)
                
                # 新しい定義を作成
                objConfig.make_config(self.config_type, self.dataset_level, self.organ_code,  myconfig)

                rebuild = False
                if myconfig_prev is None:
                    print('古いAPI定義がない')
                    rebuild = True
                else:
                    if myconfig_prev['mapping'] != myconfig['mapping']:
                        print('インデックスに変化あり', apiname)
                        # インデックスを再作成
                        rebuild = True
                    elif myconfig_prev['dataModel'] != myconfig['dataModel']:
                        print('データモデルに変化あり', apiname)
                        # 取り込むべき項目が変わった可能性あり
                        # データ再投入=>インデックスごと削除
                        rebuild = True


                if myconfig != myconfig_prev:
                    print('myconfigを更新する', apiname)
                    objConfig.set_config(myconfig)
                else:
                    print('変化なし', apiname)

                result = myconfig
            else:
                print('データセット定義JSON整形エラー')

        except Exception as e:
            print('update_myconfig', e)
        return result

    def reshape(self, prefix, data):
        myconfig = None
        try:
            if data is not None:
                #print('reshape', data)
                text = data['apiname']
                if prefix is not None and not text.startswith(prefix):
                    data['apiname'] = f'{prefix}_{text}'

                text = data['index']
                if prefix is not None and not text.startswith(prefix):
                    data['index'] = f'{prefix}_{text}'

                for key in data['dataModel']:
                    item = data['dataModel'][key]
                    if 'rename_list' in item:
                        token = []
                        text = item['rename_list'].strip()
                        if text != '':
                            token = text.split(';')
                        item['rename_list'] = token

                # text to boolean
                for field in [ 'tag_only', 'select_latest']:
                    flag = True
                    if data[field].lower() == 'false':
                        flag = False
                    data[field] = flag

                # text to list
                for field in [ 'dataset_title_list', 'format_list' ]:
                    token = []
                    text = data[field].strip()
                    if text != '':
                        token = text.split(';')
                    data[field] = token

                # tag_list ２重配列
                tag_set_list = []
                tag_list = data['tag_list'].strip()
                if tag_list != '':
                    tags_list = tag_list.split('/')
                    for tags in tags_list:
                        text = tags.strip()
                        if text != '':
                            tag_set = text.split(';')
                            tag_set_list.append(tag_set)

                data['tag_list'] = tag_set_list

                myconfig = data

        except Exception as e:
            print('reshape', e)
        return myconfig

    def search_configs(self):
        result = None
        try:
            objConfig = MyConfig()
            result = objConfig.search_index_list(self.config_type, organ_code=self.organ_code)
                        
        except Exception as e:
            print('search_configs', e)
        return result

    def get_config(self, apiname):
        result = None
        try:
            objConfig = MyConfig()
            myconfig = objConfig.get_config(apiname)
            if myconfig is not None and myconfig['dataset_type'] == self.config_type:
                result = myconfig

        except Exception as e:
            print('get_config', e)
        return result

    def delete_config(self, apiname):
        result = False
        try:
            objConfig = MyConfig()
            myconfig = objConfig.get_config(apiname)
            if myconfig is not None:
                if myconfig['dataset_type'] == self.config_type:
                    # delete config and data
                    MyConfig.delete_config(apiname)
                    result = {
                        'status': 'OK',
                        'message': '指定されたデータセット定義を削除しました'
                    }
                else:
                    print('can not delete config', apiname)
                    result = {
                        'status': 'ERROR',
                        'message': '共通のデータセット定義は削除できません'
                    }
            else:
                print('unknown config', apiname)
                result = {
                    'status': 'ERROR',
                    'message': '指定されたデータセット定義が見つかりません'
                }

        except Exception as e:
            print('delete_myconfig', e)
        return result

    def delete_all_config(self):
        result = False
        try:
            # 現在のデータセットタイプに登録されているすべてのデータセットの情報を削除する
            config_list = self.get_config_list()
            for myconfig in config_list:
                apiname = myconfig['apiname']
                # delete config and data
                MyConfig.delete_config(apiname)

            result = True

        except Exception as e:
            print('delete_all_config', e)
        return result

    def get_config_list(self):
        result = None
        try:
            result = MyConfig.get_dataset_type_config_list(self.config_type, self.organ_code)

        except Exception as e:
            print('get_config_list', e)
        return result


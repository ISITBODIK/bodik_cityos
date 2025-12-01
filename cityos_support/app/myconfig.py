import datetime
import time

import myes

class MyConfig:

    TIMESTAMP_FIELD = '_updated_at'

    # dataset type
    TYPE_MSDS = 'msds'              # msds      自治体標準ODS
    TYPE_MYAPI = 'myapi'            # myapi     独自APIの基底クラスID
    TYPE_CMAPI = 'cmapi'            # mcmpi     全国共通API
    TYPE_LGAPI = 'lgapi'            # lgapi     自治体のMyAPI
    TYPE_DPAPI = 'dpapi'            # dpapi     データ基盤のMyAPI

    common_type = 'standard'

    field_type_dict = {
        'Lgcode': { 'type': 'keyword' },
        'Lgname': { 'type': 'keyword' },
        'Keyword': { 'type': 'keyword' },
        'String': { 'type': 'keyword' },
        'List': { 'type': 'keyword' },
        'Integer': { 'type': 'long' },
        'Float': { 'type': 'float' },
        'Date': { 'type': 'date', 'format': 'yyyy-MM-dd' },
        'Time': { 'type': 'date', 'format': 'HH:mm' },
        'Address': { 'type': 'keyword' },
        'Tel': { 'type': 'keyword' },
        'Url': { 'type': 'keyword' },
        'Umu': { 'type': 'keyword' },
        'Kahi': { 'type': 'keyword' },
        'Object': { 'type': 'object' },
        'Point': { 'type': 'geo_point' },       # 距離計算のためには、geo_pointが必要
        'Line': { 'type': 'geo_shape' },
        'Polygon': { 'type': 'geo_shape' },
        'Location.lat': { 'type': 'Float' },
        'Location.lon': { 'type': 'Float' }
    }

    filter_dict = {
        'Lgcode': "term",           # 2025-09-01 keyword: wildcard to term
        'Lgname': "wildcard",
        'Keyword': "term",          # 2025-09-01 keyword: wildcard to term
        'String': "wildcard",
        'List': "list",
        'Integer': "range",
        'Float': "range",
        'Date': "range",
        'Time': "range",
        'Address': "wildcard",
        'Tel': "wildcard",
        'Url': "wildcard",
        'Umu': "wildcard",
        'Kahi': "wildcard",
        'Object': None,
        'Point': None,
        'Polygon': None,
        'Location.lat': "term",
        'Location.lon': "term"
    }

    config = {
        'index': 'myconfig',
        "mapping": {
            "mappings": {
                "properties": {
                    "dataset_type": { "type": "keyword" },      # standard, msds
                    "dataset_level": { "type": "keyword" },     # 1:基本編、2:応用編
                    "dp_name": { "type": "keyword" },           # データ基盤独自用
                    "organ_code": { "type": "keyword" },        # 自治体独自用

                    "apiname": { "type": "keyword" },           # name of myapi
                    "entity_type": { "type": "keyword" },           # for fiware
                    "Fiware-Service": { "type": "keyword" },        # for fiware
                    "Fiware-ServicePath": { "type": "keyword" },    # for fiware

                    "index": { "type": "keyword" },
                    "display_name": { "type": "keyword" },
                    "geometry": { "type": "keyword" },

                    "dataModel": { "type": "object" },
                    "fields": { "type": "object" },
                    "mapping": { "type": "object" },
                    "must_fields": { "type": "keyword" },        # 2023-05-21 added, array of string

                    # option
                    "tag_only": { "type": "keyword" },
                    "select_latest": { "type": "keyword" },

                    # dataset                    
                    "dataset_title": { "type": "keyword" },
                    "tag_list": { "type": "keyword" },
                    # resource
                    "resource_title": { "type": "keyword" },
                    "resource_filename": { "type": "keyword" },
                    "format_list": { "type": "keyword" }
                }
            }
        }
    }

    @classmethod
    def delete_index(cls):
        result = False
        try:
            myes.delete_index(cls.config)
            result = True
        except Exception as e:
            print('delete_index', e)

        return result

    @classmethod
    def get_dataset_type_config_list(cls, dataset_type, organ_code = None):
        result = None
        try:
            qs = {
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "dataset_type": dataset_type }}
                        ]
                    }
                },
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }

            if organ_code is not None:
                qs['query']["bool"]["must"].append(
                    { "term": { "organ_code": organ_code }}
                )

            result = myes.search_document(cls.config, qs)
        
        except Exception as e:
            print('get_dataset_type_config_list', e)

        return result

    #-----------------------------------------------------
    # 推奨データセットと自治体標準データセットの切り替え
    #-----------------------------------------------------
    @classmethod
    def get_mystandard_config_list(cls):
        result = None
        try:
            if cls.common_type == 'msds':
                result = cls.get_msds_config_list()
            else:
                result = cls.get_standard_config_list()

        except Exception as e:
            print('get_mystandard_config_list', e)
        return result

    #-----------------------------------------------------
    # 推奨データセット
    #-----------------------------------------------------
    @classmethod
    def get_standard_config_list(cls):
        index_list = None
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "standard" }
                },
                "sort": [
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }
            index_list = myes.search_document(cls.config, qs)
        except Exception as e:
            print('get_standard_config_list', e)
        return index_list

    #-----------------------------------------------------
    # 自治体標準データセット
    #-----------------------------------------------------
    @classmethod
    def get_msds_config_list(cls):
        index_list = None
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "msds" }
                },
                "sort": [
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }
            index_list = myes.search_document(cls.config, qs)
        except Exception as e:
            print('get_msds_config_list', e)
        return index_list

    def delete_myconfig(self, apiname):
        result = False
        try:
            doc_id = apiname
            myconfig = myes.get_source(self.config, doc_id)
            if myconfig is not None:
                myes.delete_index(myconfig)
                myes.delete_document_id(self.config, doc_id)
                result = True
            else:
                print('unknown apiname', apiname)

        except Exception as e:
            print('ERROR delete_myconfig', e)
        return result

    def __init__(self):
        try:
            self.dp_name = None
            self.init_index()

        except Exception as e:
            print('ERROR MyConfig.init', e)
        return
    
    def init_index(self):
        try:
            if myes.exists(self.config) == False:
                myes.create_index(self.config)
                myes.update_index_setting(self.config)

        except Exception as e:
            print('ERROR init_index', e)

    def set_dp(self, dp_name):
        result = False
        try:
            self.dp_name = dp_name
            result = True
        except Exception as e:
            print('set_dp', e)
        return result

    def get_config(self, apiname):
        result = None
        try:
            doc_id = f'{apiname}'
            myconfig = myes.get_source(self.config, doc_id)
            # 2024-05-14 長崎県用パッチ
            if self.dp_name == 'nagasaki':
                if apiname == 'preschool':
                    myconfig['dataModel']['連絡先備考（その他、SNSなど）']['type'] = 'String'
                    myconfig['dataModel']['子供預かり開所時間']['type'] = 'String'      # 2024-10-29 String to Time
                    myconfig['dataModel']['子供預かり閉所時間']['type'] = 'String'      # 2024-10-29 String to Time
            
            result = myconfig

        except Exception as e:
            print('get_config', e)
        return result

    def get_entity_config(self, entity_type):
        result = None
        try:
            qs = {
                'query': {
                    "term": { "entity_type": entity_type }
                }
            }
            response = myes.search_document(self.config, qs)
            if response is not None:
                print('get_entity_config', response)
                result = response[0]

        except Exception as e:
            print('get_entity_config', e)
        return result

    def set_config(self, doc):
        result = False
        try:
            apiname = doc['apiname']
            doc_id = f'{apiname}'

            if myes.get_source(self.config, doc_id):
                myes.delete_document_id(self.config, doc_id)
                time.sleep(1)

            result = myes.create_document(self.config, doc_id, doc)

        except Exception as e:
            print('set_config', e)
        return result

    # dataModelからmyconfigを構築する
    def make_config(self, dataset_type, dataset_level, organ_code, myconfig):
        try:
            fields = {}
            properties = {}

            isLat = False
            isLon = False

            dataModel = myconfig['dataModel']
            for field in dataModel:
                item = dataModel[field]
                field_name = item['field_name']
                
                field_type = item['type']
                if field_type not in self.field_type_dict:
                    field_type = 'Keyword'
                
                myfilter = None
                if field_type in self.filter_dict:
                    myfilter = self.filter_dict[field_type]

                # fields
                fields[field_name] = {
                    "field_type": field_type,
                    "filter": myfilter
                }

                # properties of mapping
                properties[field_name] = self.field_type_dict[field_type]


            # 管理情報
            fields['resource_organ_code'] = {
                "field_type": "String",
                "filter": "wildcard"
            }
            fields['resource_id'] = {
                "field_type": "String",
                "filter": "wildcard"
            }
            # 2025-09-01 追加
            fields[self.TIMESTAMP_FIELD] = {
                "field_type": "Date",
                "filter": "range"
            }
            
            properties['resource_organ_code'] = self.field_type_dict['Keyword']
            properties['resource_id'] = self.field_type_dict['Keyword']
            # 2025-08-19 added
            properties[self.TIMESTAMP_FIELD] = self.field_type_dict['Keyword']

            # location
            geometry = myconfig['geometry']
            if geometry != '':
                fields['lat'] = {
                    'field_type': 'Location.lat',
                    'filter': 'wildcard'
                }

                fields['lon'] = {
                    'field_type': 'Location.lon',
                    'filter': 'wildcard'
                }

                if geometry == 'Point':
                    if 'lat' in properties:
                        del properties['lat']
                    if 'lon' in properties:
                        del properties['lon']
                    properties['geometry'] = self.field_type_dict['Point']
                elif geometry == 'Polygon':
                    properties['geometry'] = self.field_type_dict['Polygon']
                elif geometry == 'Line':
                    properties['geometry'] = self.field_type_dict['Line']

            myconfig['fields'] = fields
            myconfig['mapping'] = {
                'mappings': {
                    'properties': properties
                }
            }
            myconfig['dataset_type'] = dataset_type
            myconfig['dataset_level'] = dataset_level
            myconfig['organ_code'] = organ_code

        except Exception as e:
            print('make_config', e)


    def search_index_list(self, dataset_type, dp_name=None, organ_code = None):
        result = None
        try:
            condition = [
                { "term": { "dataset_type": dataset_type }}
            ]
            if dp_name is not None:
                condition.append(
                    { "term": { "dp_name": dp_name }}
                )
            if organ_code is not None:
                condition.append(
                    { "term": { "organ_code": organ_code }}
                )

            qs = {
                "query": {
                    "bool": {
                        "must": condition
                    }
                },
                "sort": [
                    { "dataset_level": "asc" },
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]  
            }
            print(qs)
            index_list = myes.search_document(self.config, qs)
            result = index_list

        except Exception as e:
            print('search_myapi_index_list', e)
        return result
    
    
    #------------------------------------------------------
    #   推奨データセットと自治体標準データセットの使い分け
    #------------------------------------------------------
    def get_mystandard_index_list(self):
        result = None
        try:
            if self.common_type == 'msds':
                result = self.get_msds_index_list()
            else:
                result = self.get_standard_index_list()

        except Exception as e:
            print('get_mystandard_index_list', e)
        return result

    def listup_mystandard(self):
        result = None
        try:
            if self.common_type == 'msds':
                result = self.listup_msds()
            else:
                result = self.listup_standard()
            
        except Exception as e:
            print('listup_mystandard', e)
        return result

    #------------------------------------------------------
    #   共通データセット
    #------------------------------------------------------
    def get_common_index_list(self):
        index_list = None
        try:
            index_list = []

            list_mystandard = self.get_mystandard_index_list()
            index_list.extend(list_mystandard)

            list_predefined = self.get_predefined_index_list()
            index_list.extend(list_predefined)

        except Exception as e:
            print('get_common_index_list', e)
        return index_list

    def listup_common(self):
        result = []
        try:
            list_mystandard = self.listup_mystandard()
            result.extend(list_mystandard)

            list_predefined = self.listup_predefined()
            result.extend(list_predefined)

        except Exception as e:
            print('listup_common', e)
        return result

    def delete_api_record(self, apiname):
        result = False
        try:
            config_list = []
            if apiname is None:
                config_list = self.listup_mystandard()
            else:
                myconfig = self.get_config(apiname)
                if myconfig is not None:
                    config_list.append(myconfig)

            for myconfig in config_list:
                myes.delete_index(myconfig)
                myes.create_index(myconfig)

            result = True

        except Exception as e:
            print('delete_api_record', e)
        return result

    #------------------------------------------------------
    #   推奨データセット
    #------------------------------------------------------
    def get_standard_index_list(self):
        index_list = None
        try:
            index_list = self.get_msds_index_list()

        except Exception as e:
            print('get_standard_index_list', e)
        return index_list

    def listup_standard(self):
        result = []
        try:
            result = self.listup_msds()

        except Exception as e:
            print('listup_standard', e)
        return result

    #------------------------------------------------------
    #   自治体標準データセット
    #------------------------------------------------------
    def get_msds_index_list(self):
        index_list = None
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "msds" }
                },
                "sort": [
                    { "dataset_level": "asc" },
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]                
            }
            print(qs)
            index_list = myes.search_document(self.config, qs)

        except Exception as e:
            print('get_msds_index_list', e)
        return index_list

    def listup_msds(self):
        result = []
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "msds" }
                },
                "sort": [
                    { "apiname": "asc" }
                ]
            }
            result = myes.search_document(self.config, qs)

        except Exception as e:
            print('listup_msds', e)
        return result

    #------------------------------------------------------
    #   共通データセット
    #------------------------------------------------------
    def get_predefined_index_list(self):
        index_list = None
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "predefined" }
                },
                "sort": [
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }
            index_list = myes.search_document(self.config, qs)

        except Exception as e:
            print('get_predefined_index_list', e)
        return index_list

    def listup_predefined(self):
        result = []
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "predefined" }
                },
                "sort": [
                    { "apiname": "asc" }
                ]
            }
            result = myes.search_document(self.config, qs)

        except Exception as e:
            print('listup_predefined', e)
        return result

    #------------------------------------------------------
    #   自治体独自データセット
    #------------------------------------------------------
    def get_lgapi_index_list(self, organ_code):
        index_list = None
        try:
            qs = {
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "dataset_type": self.TYPE_LGAPI }},
                            { "term": { "organ_code": organ_code }}
                        ]
                    }
                },
                "sort": [
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }
            print('get_lgapi_index_list', qs)
            index_list = myes.search_document(self.config, qs)

        except Exception as e:
            print('get_lgapi_index_list', e)
        return index_list

    def listup_lgpi(self, organ_code):
        result = []
        try:
            qs = {
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "dataset_type": self.TYPE_LGAPI }},
                            { "term": { "organ_code": organ_code }}
                        ]
                    }
                },
                "sort": [
                    { "apiname": "asc" }
                ]
            }
            print('listup_dpapi', qs)
            result = myes.search_document(self.config, qs)

        except Exception as e:
            print('listup_dpapi', e)
        return result

    #------------------------------------------------------
    #   データ基盤独自データセット
    #------------------------------------------------------
    def get_dpapi_index_list(self, dp_name):
        index_list = None
        try:
            qs = {
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "dataset_type": "dpapi" }},
                            { "term": { "dp_name": dp_name }}
                        ]
                    }
                },
                "sort": [
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }
            print('get_dpapi_index_list', qs)
            index_list = myes.search_document(self.config, qs)

        except Exception as e:
            print('get_dpapi_index_list', e)
        return index_list

    def listup_dpapi(self, dp_name):
        result = []
        try:
            qs = {
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "dataset_type": "dpapi" }},
                            { "term": { "dp_name": dp_name }}
                        ]
                    }
                },
                "sort": [
                    { "apiname": "asc" }
                ]
            }
            print('listup_dpapi', qs)
            result = myes.search_document(self.config, qs)

        except Exception as e:
            print('listup_dpapi', e)
        return result

    #------------------------------------------------------
    #   トライアルデータセット
    #------------------------------------------------------
    def get_trial_index_list(self):
        index_list = None
        try:
            qs = {
                "query": {
                    "term": { "dataset_type": "trial" }
                },
                "sort": [
                    { "apiname": "asc" }
                ],
                "_source": [ "dataset_type", "apiname", "display_name", "geometry", "index", "organ_code" ]
            }
            index_list = myes.search_document(self.config, qs)

        except Exception as e:
            print('get_trial_index_list', e)
        return index_list

    #------------------------------------------------------
    #   管理
    #------------------------------------------------------
    def groupby(self, apiname):
        result = None
        try:
            myconfig = self.get_config(apiname)
            if myconfig is not None:
                qs = {
                    "size": 0,
                    "aggs": {
                        "groupBy": {
                            "terms": {
                                "field": "resource_organ_code",
                                "size": 5000
                            },
                        }
                    }
                }
                result = myes.groupby(myconfig, qs)
        except Exception as e:
            print('groupby', e)
        return result

    def delete_record(self, apiname, organ_code):
        result = False
        try:
            myconfig = self.get_config(apiname)
            if myconfig is not None:
                qs = {
                    "query": {
                        "bool": {
                            "must": [
                                { "term": { "resource_organ_code": organ_code }}
                            ]
                        }
                    }
                }
                myes.delete_document(myconfig, qs)
                result = True

        except Exception as e:
            print('delete_record', e)
        return result

    def manage_get_myapi_list(self, dataset_type):
        result = None
        try:
            if dataset_type != self.TYPE_MSDS:
                apiname_list = self.get_dataset_type_apiname_list(dataset_type)
                if apiname_list is not None:
                    output = []
                    for info in apiname_list:
                        output.append(info['apiname'])
                    result = output

        except Exception as e:
            print('manage_get_myapi_list', e)
        return result

    def manage_get_myapi_config(self, apiname):
        result = None
        try:
            doc_id = apiname
            source = myes.get_source(self.config, doc_id)
            result = source

        except Exception as e:
            print('manage_get_myapi_config', e)
        return result

    def manage_set_myapi_config(self, apiname, myconfig):
        result = None
        try:
            doc_id = apiname
            source = myes.get_source(self.config, doc_id)
            if source is not None:
                # update
                update_doc = {
                    'doc': myconfig
                }
                result = myes.update_document(self.config, doc_id, update_doc)
            else:
                # create
                doc = myconfig
                result = myes.create_document(self.config, doc_id, doc)

        except Exception as e:
            print('manage_set_myapi_config', e)
        return result

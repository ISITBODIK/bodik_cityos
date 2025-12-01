import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

from elasticsearch import Elasticsearch, helpers
import math
from math import *

from myconfig import MyConfig

import es_common

from env import es_server

class History:

    def __init__(self):
        try:
            self.myconfig = None
            self.es = None
            self.es = Elasticsearch(es_server)
        except Exception as e:
            print('History.init', e)
    
    def search(self, params):
        result = None
        try:
            obj = MyConfig()
            if 'apiname' in params:
                apiname = params['apiname']
                self.myconfig = obj.get_config(apiname)
            elif 'entity_type' in params:
                entity_type = params['entity_type']
                self.myconfig = obj.get_entity_config(entity_type)

            if self.myconfig is not None:
                print('myconfig', self.myconfig)                      
                geometry_type = self.myconfig['geometry']
                print('params', params)
                query = MyQuery()
                if 'select_type' not in params:
                    params['select_type'] = 'data'
                if 'maxResults' not in params:
                    params['maxResults'] = 10
                if geometry_type != '':
                    if 'distance' not in params:
                        params['distance'] = 2000
                
                self.set_query_params(query, params)

                q = query.getBody()
                res_count = self.es.count(index=self.myconfig['index'], body=q)
                counts = None
                if res_count:
                    counts = res_count['count']
                
                selecttype = es_common.adjustSelectType(params['select_type'])
                limit = es_common.adjustMaxResults(params['maxResults'])

                myresult = es_common.MyResult(self.myconfig['apiname'])
                myresult.setMetadata('selectType', selecttype)
                myresult.setMetadata('totalCount', counts)

                if selecttype != 'COUNT':
                    if geometry_type == 'Point':
                        if 'lat' in params and 'lon' in params:
                            query.sortDistance(params['lat'], params['lon'])
                            q = query.getBody()
                    else:
                        query.sortTimestamp()
                        q = query.getBody()

                    print('es.search', q)

                    response = self.search_document(q, limit)
                    if response:
                        myresult.setMetadata('count', len(response))

                        geojson = es_common.GeoJson()
                        properties = self.myconfig['mapping']['mappings']['properties']
                        #for obj in response['hits']['hits']:
                        for obj in response:
                            src = obj['_source']
                            #print('src', src)
                            
                            feature = es_common.Feature()
                            for field in properties:
                                if field in ['location', 'geometry']:
                                    pass
                                else:
                                    if field in src:
                                        feature.addProperty(field, src[field])

                            if geometry_type != '':
                                if 'sort' in obj:
                                    distance = obj['sort'][0]
                                    feature.addProperty('distance', distance)

                            if selecttype == 'GEOMETRY':
                                #print('GEOMETRY', src)

                                if 'geometry' in src and src['geometry']:
                                    geometry = src['geometry']
                                    if geometry_type == 'Point':
                                        lat = geometry['lat']
                                        lon = geometry['lon']
                                        geometry = {
                                            'type': 'Point',
                                            'coordinates': [ lon, lat ]
                                        }

                                    feature.setGeometry(geometry)

                            geojson.addFeature(feature)

                        myresult.setResultSet(geojson.getValue())

                result = myresult.getValue()

            else:
                print('APIを特定できません', params)

        except Exception as e:
            print('search', e)
        return result

    def set_query_params(self, query, params):
        try:
            geometry = self.myconfig['geometry'].lower()
            fields = self.myconfig['fields']
            #print('fields', fields)
            
            for field in fields:
                if geometry == '' or field not in ['lat', 'lon']:
                    if field in params and params[field] is not None:
                        info = fields[field]
                        query.addFilter(params, field, info)

            # 地理計算
            if geometry == 'point':
                if 'lat' in params and 'lon' in params and 'distance' in params:
                    lat = params['lat']
                    lon = params['lon']
                    distance = params['distance']
                    # 距離検索
                    query.addDistanceFilter(lat, lon, distance)
            elif geometry == 'polygon' or geometry == 'multipolygon':
                if 'lat' in params and 'lon' in params:
                    lat = params['lat']
                    lon = params['lon']
                    # 内包検索
                    query.addContainsFilter(lat, lon)
            elif geometry == 'line':
                if 'lat' in params and 'lon' in params and 'distance' in params:
                    lat = params['lat']
                    lon = params['lon']
                    distance = params['distance']
                    # 範囲検索（円と重なる対象を検索する）
                    query.addCircleFilter(lat, lon, distance)

        except Exception as e:
            print('set_query_params', self.myconfig['apiname'], e)

        return

    ############################
    #   ドキュメント検索
    ############################
    def search_document(self, q, limit):
        result = []
        sid = None
        try:
            finish = False
            count = 0
            page = self.es.search(index=self.myconfig['index'], body=q, size=1000, scroll='1s')
            if page:
                sid = page['_scroll_id']
                scroll_size = len(page['hits']['hits'])

                while scroll_size > 0:
                    for obj in page['hits']['hits']:
                        result.append(obj)
                        count += 1
                        if count >= limit:
                            finish = True
                            break

                    if finish:
                        break
                    else:
                        # 次のページを取得
                        page = self.es.scroll(scroll_id=sid, scroll='1s')
                        if page:
                            # update scroll id
                            sid = page['_scroll_id']
                            # get number of results that it returned in the last scroll
                            scroll_size = len(page['hits']['hits'])

                        else:
                            # error
                            print('search(scroll)2 failed')
                            break
            else:
                print('search(scroll) failed')

            print('search_document', len(result))

        except Exception as e:
            print(self.myconfig['index'], 'search_document ERROR:', e)

        return result

class MyQuery:

    ELLIPSOID_GRS80 = 1 # GRS80
    ELLIPSOID_WGS84 = 2 # WGS84

    # 楕円体別の長軸半径と扁平率
    GEODETIC_DATUM = {
        ELLIPSOID_GRS80: [
            6378137.0,         # [GRS80]長軸半径
            1 / 298.257222101, # [GRS80]扁平率
        ],
        ELLIPSOID_WGS84: [
            6378137.0,         # [WGS84]長軸半径
            1 / 298.257223563, # [WGS84]扁平率
        ],
    }

    ITERATION_LIMIT = 1000
    TIMESTAMP_FIELD = '_updated_at'     # cityos_subsc で追加される管理用項目

    body = {}
    filter = []
    sort_section = []
    savefilter = []

    def __init__(self):
        self.body = {}
        self.filter = []
        self.sort_section = []
        self.savefilter = []

    def getBody(self):

        ## 初期化
        self.body = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    }
                }
            }
        }
        
        if len(self.filter) > 0:
            self.body["query"]["bool"]["filter"] = self.filter

        if len(self.sort_section) > 0:
            self.body["sort"] = self.sort_section
    
        return self.body
    
    def addFilter(self, params, field, filter_info):

        filter_type = filter_info['filter']

        if filter_type == 'wildcard':
            self.addWildcardFilter(field, params[field])
        elif filter_type == 'term':
            self.addTermFilter(field, params[field])
        elif filter_type == 'range':
            self.addRangeFilter(field, params[field])
        elif filter_type == 'date':
            self.addDateFilter(field, params[field])
        elif filter_type == 'bool':
            self.addBooleanFilter(field, params[field])

        return

    def addTermFilter(self, key, value):

        if value is None:
            return
        else:
            term = { key : value }
            flt = {}
            flt["term"] = term

            self.filter.append(flt)
    
    def addWildcardFilter(self, key, value):

        if value is None:
            return
        else:
            wildcard = {}
            wildcard[key] = { "value": "*" + value + "*" }
            flt = {}
            flt["wildcard"] = wildcard

            self.filter.append(flt)

    def checkRangeCondition(self, value):
        result = None
        try:
            cond = {}
            for op in value:
                if op in [ 'gte', 'gt', 'lte', 'lt', 'time_zone', 'format', 'relation' ]:
                    cond[op] = value[op]
            result = cond

        except Exception as e:
            print('checkRangeCondition', e)
        return result

    def addRangeFilter(self, key, value):
        try:
            if value is None:
                return
            else:
                flt = None
                if isinstance(value, dict):
                    # from, to
                    cond = self.checkRangeCondition(value)
                    if cond is not None:
                        flt = {
                            'range': {
                                key: cond
                            }
                        }
                else:
                    flt = {
                        'term': { key: value }
                    }
                
                if flt is not None:
                    self.filter.append(flt)

        except Exception as e:
            print('addRangeFilter', e)

        return

    def addDateFilter(self, key, value, ope):
        try:
            if value is None:
                return
            else:
                flt = None
                if isinstance(value, dict):
                    # from, to
                    cond = self.checkRangeCondition(value)
                    if cond is not None:
                        flt = {
                            'range': {
                                key: cond
                            }
                        }
                else:
                    flt = {
                        'term': { key: value }
                    }
                
                if flt is not None:
                    self.filter.append(flt)

        except Exception as e:
            print('addDateFilter', e)

        return

    def addDistanceFilter(self, lat, lon, distance):
        try:
            if lat and lon and distance:
                flt = {
                    "geo_distance": {
                        "distance": str(distance) + 'm',
                        "geometry": {
                            "lat": lat,
                            "lon": lon
                        }
                    }
                }
                self.filter.append(flt)

        except Exception as e:
            print('addDistanceFilter', e)

        return

    def sortDistance(self, lat, lon):

        if lat and lon:
            flt = {
                "_geo_distance": {
                    "geometry": {
                        "lat": lat,
                        "lon": lon
                    }
                }
            }

            self.sort_section.append(flt)

    def sortTimestamp(self):

            flt = {
                self.TIMESTAMP_FIELD: "asc"
            }

            self.sort_section.append(flt)

    # (lat, lon)を含むshapeを検索
    def addContainsFilter(self, lat, lon):

        if lat and lon:
            flt = {
                "geo_shape": {
                    "geometry": {
                        "shape": {
                            "type": "point",
                            "coordinates": [lon, lat]
                        },
                        "relation": "contains"
                    }
                }
            }

            self.filter.append(flt)

    def addContainsFilter_envelop(self, lat, lon):

        if lat and lon:
            flt = {
                "geo_shape": {
                    "geometry": {
                        "shape": {
                            "type": "envelope",
                            "coordinates": [
                                [lon, lat],
                                [lon, lat]
                            ]
                        },
                        "relation": "contains"
                    }
                }
            }

            self.filter.append(flt)

    # 中心（lat, lon）半径distanceの円と交差（intersects）する図形を探す
    def addCircleFilter(self, lat, lon, distance):
        try:
            if lat and lon and distance:
                flt = {
                    "geo_shape": {
                        "shape": {      # 検索対象のフィールド名
                            "shape": {  # geo_shape検索の形状
                                "type": "circle",
                                "coordinates": [lon, lat],
                                "radius": f'{distance}m'
                            },
                            "relation": "intersects"
                        }
                    }
                }

                self.filter.append(flt)

        except Exception as e:
            print('addCircleFilter', e)
        
        return

    def addEnvelopeFilter(self, lat, lon, distance):
        try:
            # top-left: 315, bottom-right: 135
            if lat and lon and distance:
                # 外接矩形
                l = distance * math.sqrt(2)
                topleft  = self.vincenty_direct(lat, lon, l, 315)
                botright = self.vincenty_direct(lat, lon, l, 135)

                if topleft and botright:
                    flt = {
                        "geo_shape": {
                            "shape": {      # 検索対象のフィールド名
                                "shape": {  # geo_shape検索の形状
                                    "type": "envelope",
                                    "coordinates": [
                                        [topleft['lon'], topleft['lat']],
                                        [botright['lon'], botright['lat']]
                                    ]
                                },
                                "relation": "intersects"
                            }
                        }
                    }

                    self.filter.append(flt)

                else:
                    print('vincenty_direct returns None')

        except Exception as e:
            print('addEnvelopeFilter', e)
        
        return

    def vincenty_direct(self, lat, lon, distance, azimuth, ellipsoid=None):
        try:
            # 計算時に必要な長軸半径(a)と扁平率(ƒ)を定数から取得し、短軸半径(b)を算出する
            # 楕円体が未指定の場合はGRS80の値を用いる
            a, ƒ = self.GEODETIC_DATUM.get(ellipsoid, self.GEODETIC_DATUM.get(self.ELLIPSOID_GRS80))
            b = (1 - ƒ) * a

            # ラジアンに変換する(距離以外)
            φ1 = radians(lat)
            λ1 = radians(lon)
            α1 = radians(azimuth)
            s = distance

            sinα1 = sin(α1)
            cosα1 = cos(α1)

            # 更成緯度(補助球上の緯度)
            U1 = atan((1 - ƒ) * tan(φ1))

            sinU1 = sin(U1)
            cosU1 = cos(U1)
            tanU1 = tan(U1)

            σ1 = atan2(tanU1, cosα1)
            sinα = cosU1 * sinα1
            cos2α = 1 - sinα ** 2
            u2 = cos2α * (a ** 2 - b ** 2) / (b ** 2)
            A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
            B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))

            # σをs/(b*A)で初期化
            σ = s / (b * A)

            # 以下の計算をσが収束するまで反復する
            # 地点によっては収束しないことがあり得るため、反復回数に上限を設ける
            for i in range(self.ITERATION_LIMIT):
                cos2σm = cos(2 * σ1 + σ)
                sinσ = sin(σ)
                cosσ = cos(σ)
                Δσ = B * sinσ * (cos2σm + B / 4 * (cosσ * (-1 + 2 * cos2σm ** 2) - B / 6 * cos2σm * (-3 + 4 * sinσ ** 2) * (-3 + 4 * cos2σm ** 2)))
                σʹ = σ
                σ = s / (b * A) + Δσ

                # 偏差が.000000000001以下ならbreak
                if abs(σ - σʹ) <= 1e-12:
                    #print('vincenty_direct', i)
                    break
            else:
                # 計算が収束しなかった場合はNoneを返す
                print('収束しなかった')
                return None

            # σが所望の精度まで収束したら以下の計算を行う
            x = sinU1 * sinσ - cosU1 * cosσ * cosα1
            φ2 = atan2(sinU1 * cosσ + cosU1 * sinσ * cosα1, (1 - ƒ) * sqrt(sinα ** 2 + x ** 2))
            λ = atan2(sinσ * sinα1, cosU1 * cosσ - sinU1 * sinσ * cosα1)
            C = ƒ / 16 * cos2α * (4 + ƒ * (4 - 3 * cos2α))
            L = λ - (1 - C) * ƒ * sinα * (σ + C * sinσ * (cos2σm + C * cosσ * (-1 + 2 * cos2σm ** 2)))
            λ2 = L + λ1

            α2 = atan2(sinα, -x) + pi

            return {
                'lat': degrees(φ2),     # 緯度
                'lon': degrees(λ2),     # 経度
                'azimuth': degrees(α2), # 方位角
            }

        except Exception as e:
            print('vincenty_direct', e)
    
        return None
        
    def addBooleanFilter(self, key, value):

        if value is None:
            return
        else:
            flt = {}
            match = {}

            match[key] = 1
            if value:
                flt['match'] = match
            else:
                must_not = {}
                must_not['match'] = match
                onoff = {}
                onoff['must_not'] = must_not
                flt['bool'] = onoff
            
            self.filter.append(flt)

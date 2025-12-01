import math
from math import *
import myes

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

class MyQuery:

    body = {}
    filter = []
    sort_section = []
    savefilter = []

    list_separator = ';'

    def __init__(self):
        self.body = {}
        self.qLocation = {}
        self.filter = []
        self.sort_section = []
        self.savefilter = []

    def getBody(self):
        # fiware, connect with ';'
        q = ';'.join(self.filter)
        return q

    def getLocationQuery(self):
        return self.qLocation

    def addFilter(self, params, field, filter_info):
        if field in params and params[field] is not None:
            field_type = filter_info['field_type']
            if field_type == 'String':
                self.StringFilter(field, params[field])
            elif field_type == 'Integer':
                self.IntegerFilter(field, params[field])
            elif field_type == 'Float':
                self.FloatFilter(field, params[field])
            elif field_type == 'List':
                self.ListFilter(field, params[field])
            elif field_type == 'Date':
                self.FromToFilter(field, params[field])
            elif field_type == 'Time':
                self.FromToFilter(field, params[field])
            else:
                self.TextFilter(field, params[field])

        return

    def StringFilter(self, key, value):
        try:
            print(key, value)
            if value:
                self.addWildcardFilter(key, value)
        except Exception as e:
            print('StringFilter', e)

    def TextFilter(self, key, value):
        try:
            print(key, value)
            if value:
                self.addTextFilter(key, value)
        except Exception as e:
            print('TermFilter', e)

    def ListFilter(self, key, value):
        try:
            print('ListFilter', key, value)
            if value:
                print('type', type(value))
                if type(value) is str:
                    array = None
                    if self.list_separator in value:
                        array = value.split(self.list_separator)
                    else:
                        array = []
                        array.append(value)
                    print('ListFilter', array)
                    self.addListFilter(key, array)

                elif type(value) is list:
                    self.addListFilter(key, value)

        except Exception as e:
            print('NumberFilter', e)

    def IntegerFilter(self, key, value):
        try:
            print(key, value)
            if value:
                if type(value) is str:
                    if self.list_separator in value:
                        token = value.split(self.list_separator)
                        if len(token) == 2:
                            from_value = int(token[0])
                            to_value = int(token[1])
                            self.addRangeFilter(key, from_value, to_value)
                    else:
                        self.addTermFilter(key, value)

                elif type(value) is dict:
                    from_value = value['from']
                    to_value = value['to']
                    self.addRangeFilter(key, from_value, to_value)

        except Exception as e:
            print('IntegerFilter', e)

    def FloatFilter(self, key, value):
        try:
            print(key, value)
            if value:
                if type(value) is str:
                    if self.list_separator in value:
                        token = value.split(self.list_separator)
                        if len(token) == 2:
                            from_value = float(token[0])
                            to_value = float(token[1])
                            self.addRangeFilter(key, from_value, to_value)
                    else:
                        self.addTermFilter(key, value)

                elif type(value) is dict:
                    from_value = value['from']
                    to_value = value['to']
                    self.addRangeFilter(key, from_value, to_value)

        except Exception as e:
            print('FloatFilter', e)

    def FromToFilter(self, key, value):
        try:
            print(key, value)
            if value:
                if type(value) is str:
                    if self.list_separator in value:
                        token = value.split(self.list_separator)
                        if len(token) == 2:
                            self.addRangeFilter(key, token[0], token[1])
                    else:
                        self.addTermFilter(key, value)

                elif type(value) is dict:
                    from_value = value['from']
                    to_value = value['to']
                    self.addRangeFilter(key, from_value, to_value)

        except Exception as e:
            print('FromToFilter', e)


    def addWildcardFilter(self, key, value):
        if value:
            # for fiware
            flt = f'{key}~={value}'
            self.filter.append(flt)
    
    def addTextFilter(self, key, value):
        if value:
            # for fiware
            flt = f'{key}==\'{value}\''
            print('addTextFilter', flt)
            self.filter.append(flt)
    
    def addTermFilter(self, key, value):
        if value:
            # for fiware
            flt = f'{key}=={value}'
            print('addTermFilter', flt)
            self.filter.append(flt)
    
    def addListFilter(self, key, value):

        if value:
            # for fiware
            value_text = ','.join(value)
            flt = f'{key}=={value_text}'
            self.filter.append(flt)
    
    def addRangeFilter(self, key, value1, value2):

        if value1 and value2:
            flt = f'{key}=={value1}..{value2}'
        else:
            if value1:
                flt = f'{key}>={value1}'
            else:
                flt = f'{key}<={value2}'

        self.filter.append(flt)


    def addDistanceFilter(self, lat, lon, distance):
        try:
            self.qLocation = {}
            if lat and lon and distance:
                print('addDistanceFilter')
                # for fiware
                self.qLocation['georel'] = f'near;maxDistance:{distance}'
                self.qLocation['geometry'] = 'point'
                self.qLocation['coords'] = f'{lat},{lon}'
                self.qLocation['orderBy'] = f'geo:distance'
        except Exception as e:
            print('addDistanceFilter', e)        

    def sortDistance(self, lat, lon):
        #if lat and lon:
        #    flt = f'orderBy=geo:distance'
        #    self.filter.append(flt)
        return

    def addContainsFilter(self, lat,  lon, distance):

        self.qLocation = {}
        if lat and lon and distance:
            # for fiware
            self.qLocation['georel'] = f'intersectsistance:{distance}'
            self.qLocation['geometry'] = 'box'
            self.qLocation['coords'] = f'{lat},{lon}'

    def addEnvelopeFilter(self, lat, lon, distance):
        try:
            self.qLocation = {}
            if lat and lon and distance:
                topleft  = self.vincenty_direct(lat, lon, distance, 315)
                botright = self.vincenty_direct(lat, lon, distance, 135)
                #print('topleft', topleft)
                #print('botright', botright)

                if topleft and botright:
                    # for fiware
                    self.qLocation['georel'] = f'intersects'
                    self.qLocation['geometry'] = 'box'
                    self.qLocation['coords'] = [
                        [topleft['lon'], topleft['lat']],
                        [botright['lon'], botright['lat']]
                    ]

                else:
                    print('vincenty_direct returns None')

        except Exception as e:
            print('addEnvelopeFilter', e)
        
        return

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
    
class MyResult:

    result = {}

    def __init__(self, api):

        self.result = {}

        metadata = {}
        metadata['api'] = api

        self.result['metadata'] = metadata

    def setMetadata(self, key, value):
        self.result['metadata'][key] = value
    
    def setResultSet(self, obj):
        self.result['resultsets'] = obj

    def getValue(self):
        return self.result

class Feature:

    feature = {}

    def __init__(self):
        self.feature = {
            "type": "Feature",
            "properties": {}
            #"geometry": None
        }
    
    def addProperty(self, key, value):
        self.feature['properties'][key] = value
    
    def setGeometry(self, obj):
        self.feature['geometry'] = obj

    def getValue(self):
        return self.feature

class Geometry:

    def __init__(self, type_name):
        self.geometry = {
            "type": type_name
        }
    
    def addCoordinates(self, points):
        self.geometry['coordinates'] = points
    
    def getValue(self):
        return self.geometry

class GeoJson:

    geojson = {}

    def __init__(self):
        self.geojson = {
            "type": "FeatureCollection",
            "features": []
        }
    
    def addFeature(self, feature):
        self.geojson['features'].append(feature.getValue())

    def countFeatures(self):
        return len(self.geojson['features'])

    def getValue(self):
        return self.geojson


def adjustSelectType(text):

    value = 'DATA'

    try:
        word = text.upper()
        ary = [ 'COUNT', 'DATA', 'GEOMETRY']
        if word in ary:
            value = word

    except Exception as e:
        print('adjustSelectType ERROR:', e)

    return value

MAXRESULTS = 1000

def adjustMaxResults(text):

    value = 100

    try:
        num = int(text)
        if num > MAXRESULTS:
            num = MAXRESULTS

        value = num

    except Exception as e:
        print('adjustMaxResult ERROR:', e)

    return value

config_organization = {
    'index': 'ckan-organization'
}

def list_organization(es_index):

    response = None
    es = None

    try:
        q = {}

        if es_index == '*':
            q["query"] = {
                "match_all": {}
            }
        
        else:
            q["query"] = {
                "match": {
                    "index": es_index
                }
            }

        resp = myes.search_document(config_organization, q)
        response = sorted(resp, key=lambda x:x['organ_code'])

    except Exception as e:
        print('organization ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return response

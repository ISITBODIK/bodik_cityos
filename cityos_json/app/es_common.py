import math
from math import *
import myes

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

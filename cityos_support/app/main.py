from enum import Enum
from typing import Optional, List, Dict
from unittest import result
from fastapi import FastAPI, BackgroundTasks, Query, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from pydantic import BaseModel

import os
import shutil
import pathlib
from pathlib import Path
import tempfile
from tempfile import NamedTemporaryFile
import requests

import datetime
import pytz
import json
import csv
import time

import env

from keycloak import myKeycloak
from exceptions import UnauthorizedError, ForbiddenError, ServiceUnavailableError, AuthError

from test_orion import TestOrion
from test_mqtt import TestMQTT

from orion_subscription import OrionSubscription
from history import History

from myconfig import MyConfig
from configFile import configFile
from dpapi import DpAPI
from myapi import MyAPI
from map import Map

tags_metadata = [
    {
        "name": "user",
        "description": "ユーザー管理"
    },
    {
        "name": "orion",
        "description": "Orionデータ管理"
    },
    {
        "name": "keycloak",
        "description": "カスタム認証機能"
    },
    {
        "name": "manage",
        "description": "管理"
    },
    {
        "name": "myapi",
        "description": "データモデル管理"
    },
    {
        "name": "manager",
        "description": "サブスクリプション管理"
    },
    {
        "name": "history",
        "description": "履歴データ管理"
    },
    {
        "name": "geospatial",
        "description": "地理空間"
    },
    {
        "name": "mqtt",
        "description": "テストMQTT"
    },
    {
        "name": "page",
        "description": "画面"
    }
]

PATH_STATIC = str(pathlib.Path(__file__).resolve().parent / 'static')

app = FastAPI(
    title = env.API_TITLE,
    description = env.API_DESCRIPTION,
    version = env.API_VERSION,
    openapi_tags = tags_metadata
)

# CORSを回避する
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

def save_upload_file_tmp(upload_file: UploadFile):
    tmp_path: Path = ""
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = str(Path(tmp.name))
    except Exception as e:
        print("save_upload_file_tmp", e)

    finally:
        upload_file.file.close()

    info = {
        'filename': upload_file.filename,
        'tmp_filepath': tmp_path,
        'file_content_type': upload_file.content_type
    }
    print(info)

    return info

def save_url_to_tmp_file(url: str):
    tmp_path: Path = ""
    try:
        print(url)
        suffix = '.xlsx'
        res = requests.get(url)
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(res.content)

        tmp_path = str(Path(tmp.name))
        print(tmp_path)

    except Exception as e:
        print("save_url_to_tmp_file", e)

    return tmp_path

###################################
#   管理
###################################
@app.get('/manage/jwt', tags=['manage'])
def manage_make_jwt(clientid: str, username: str, password: str):
    result = None
    try:
        obj = myKeycloak()
        result = obj.get_jwt(clientid, username, password)

    except Exception as e:
        print('manage_make_jwt', e)
    return result

###################################
#   カスタム認証機能
###################################
# emqxのカスタムプラグインから呼び出される。カスタムプラグインのUIに従う必要あり。
# 内部的にはusernameとpasswordしか使わない
@app.post('/mqtt/auth', tags=['keycloak'])
def auth_client(#request: Request,
        clientid: str = Form(...),      # MQTT clientid, not keycloak clientid
        username: str = Form(...),
        password: str = Form(...),
        peerhost: Optional[str] = Form(None),
        sockport: Optional[int] = Form(None),
        protocol: Optional[str] = Form(None),
        mountpoint: Optional[str] = Form(None)):
    
    result = False
    try:
        print('/mqtt/auth', clientid, username, password)
        obj = myKeycloak()
        result = obj.mqtt_auth(clientid, username, password)
        
    except Exception as e:
        print('auth_mqtt_client', e)
        raise HTTPException(status_code=401, detail="Unauthorized") # 認証失敗
    
    return result

@app.post('/mqtt/acl', tags=['keycloak'])
def check_acl(#request: Request,
        access: str = Form(...), # subscribe, publish, all
        clientid: str = Form(...),      # MQTT clientid, not keycloak clientid
        username: str = Form(...),
        topic: str = Form(...),
        peerhost: Optional[str] = Form(None),
        sockport: Optional[int] = Form(None),
        protocol: Optional[str] = Form(None),
        mountpoint: Optional[str] = Form(None)):
    result = False
    try:
        print('/mqtt/acl', access, clientid, username, topic)
        obj = myKeycloak()
        result = obj.mqtt_acl(access, clientid, username, topic)
    except Exception as e:
        print('check_mqtt_acl', e)
        raise HTTPException(status_code=401, detail="Unauthorized") # 認証失敗

    return result

@app.post('/kong/auth', tags=['keycloak'])
def auth_client(#request: Request,
        #clientid: str = Form(...),      # MQTT clientid, not keycloak clientid
        username: str = Form(...),
        password: str = Form(...),
        #peerhost: Optional[str] = Form(None),
        #sockport: Optional[int] = Form(None),
        #protocol: Optional[str] = Form(None),
        #mountpoint: Optional[str] = Form(None)
        ):
    
    result = False
    try:
        print('/kong/auth', username, password)
        obj = myKeycloak()
        result = obj.kong_auth(username, password)
        
    except Exception as e:
        print('auth_kong_client', e)
        raise HTTPException(status_code=401, detail="Unauthorized") # 認証失敗
    
    return result

@app.post('/kong/acl', tags=['keycloak'])
def check_acl(#request: Request,
        access: str = Form(...), # subscribe, publish, all
        clientid: str = Form(...),      # MQTT clientid, not keycloak clientid
        username: str = Form(...),
        topic: str = Form(...),
        peerhost: Optional[str] = Form(None),
        sockport: Optional[int] = Form(None),
        protocol: Optional[str] = Form(None),
        mountpoint: Optional[str] = Form(None)):
    result = False
    try:
        print('/kong/acl', access, clientid, username, topic)
        obj = myKeycloak()
        result = obj.kong_acl(access, clientid, username, topic)
    except Exception as e:
        print('check_kong_acl', e)
        raise HTTPException(status_code=401, detail="Unauthorized") # 認証失敗

    return result

###################################
#   Orion
###################################
@app.get('/orion/version', tags=['orion'])
def get_orion_version():
    result = False
    try:
        obj = TestOrion(None)
        result = obj.get_version()

    except Exception as e:
        print('get_orion_version', e)
    return result

@app.get('/orion/data', tags=['orion'])
def get_orion_data(apiname: str, id: str):
    result = False
    try:
        obj = TestOrion(apiname)
        result = obj.get_data(id)
    except Exception as e:
        print('get_orion_data', e)
    return result

@app.get('/orion/datas', tags=['orion'])
def search_orion_data(apiname: str):
    result = False
    try:
        obj = TestOrion(apiname)
        result = obj.search_data()
    except Exception as e:
        print('search_orion_data', e)
    return result

@app.post('/orion/data', tags=['orion'])
def set_orion_data(apiname: str, data: dict):
    result = False
    try:
        obj = TestOrion(apiname)
        result = obj.set_data(data)
    except Exception as e:
        print('set_orion_data', e)
    return result

@app.delete('/orion/datas', tags=['orion'])
def delete_orion_all_data(apiname: str):
    result = False
    try:
        obj = TestOrion(apiname)
        result = obj.delete_all_data()

    except Exception as e:
        print('delete_orion_all_data', e)
    return result

###################################
#   データモデル管理
###################################
@app.delete('/myconfig', tags=['myapi'])
def delete_myconfig_index():
    result = None
    try:
        result = MyConfig().delete_index()

    except Exception as e:
        print('delete_myconfig_index', e)
    return result

@app.get('/myapi/config', tags=['myapi'])
def get_myapi_config(apiname: str):
    result = None
    try:
        obj = MyConfig()
        result = obj.get_config(apiname)

    except Exception as e:
        print('get_myapi_config', e)
    return result

@app.get('/myapi/entity_type', tags=['myapi'])
def get_entity_myapi_config(entity_type: str):
    result = None
    try:
        obj = MyConfig()
        result = obj.get_entity_config(entity_type)

    except Exception as e:
        print('get_entity_myapi_config', e)
    return result

@app.delete('/myapi/config', tags=['myapi'])
def delete_myapi_config(apiname: str):
    result = None
    try:
        obj = MyConfig()
        result = obj.delete_myconfig(apiname)

    except Exception as e:
        print('delete_myapi_config', e)
    return result

@app.post('/myapi/dpapi', tags=['myapi'])
def set_dpapi(config_file: UploadFile=File(...)):
    result = None
    try:
        config = None
        info = save_upload_file_tmp(config_file)
        tmp_file = info['tmp_filepath']
        with open(tmp_file) as f:
            config = json.load(f)

        if config is not None:
            obj = DpAPI()
            result = obj.make_config(config)
        else:
            print('can not load config json file')
            
    except Exception as e:
        print('set_dpapi', e)
    return result

@app.get('/myapi/data', tags=['myapi'])
def search_myapi_es_data(apiname: str):
    result = False
    try:
        obj = MyAPI()
        result = obj.search_es_data(apiname)
    
    except Exception as e:
        print('make_myapi_es_index', e)
    return result

@app.post('/myapi/index', tags=['myapi'])
def make_myapi_es_index(apiname: str):
    result = False
    try:
        obj = MyAPI()
        result = obj.make_es_index(apiname)
    
    except Exception as e:
        print('make_myapi_es_index', e)
    return result

@app.delete('/myapi/index', tags=['myapi'])
def delete_myapi_es_index(apiname: str):
    result = False
    try:
        obj = MyAPI()
        result = obj.delete_es_index(apiname)
    
    except Exception as e:
        print('delete_myapi_es_index', e)
    return result

###################################
#   テスト MQTT
###################################
@app.post('/mqtt/publish', tags=['mqtt'])
def mqtt_publish(username: str, password: str, topic: str, data: dict):
    result = False
    try:
        obj = TestMQTT()
        result = obj.publish(username, password, topic, data)

    except Exception as e:
        print('mqtt_publish', e)
    return result

status_task_subscribe = False

@app.get('/mqtt/subscribe/status', tags=['mqtt'])
def check_mqtt_subscribe_status():
    global status_task_subscribe
    result = None
    try:
        if status_task_subscribe:
            result = {
                'status': True,
                'message': 'on subscribe....'
            }
        else:
            result = {
                'status': False,
                'message': 'no subscribe....'
            }

    except Exception as e:
        print('check_mqtt_subscribe_status', e)
    return result

def task_subscribe(topic, username, password):
    global status_task_subscribe
    try:
        status_task_subscribe = True
        obj = TestMQTT()
        obj.subscribe(topic, username, password)
        print('subscribe end')

    except Exception as e:
        print('Exception, task_subscribe', e)
    status_task_subscribe = False
    
@app.get('/mqtt/subscribe', tags=['mqtt'])
def mqtt_subscribe(topic: str, username: str, password: str, background_tasks: BackgroundTasks):
    global status_task_subscribe
    result = None
    try:
        if status_task_subscribe:
            result = {
                'status': False,
                'message': 'on subscribe...'
            }
        else:
            background_tasks.add_task(task_subscribe, topic, username, password)
            result = {
                'status': True,
                'message': 'start subscribe....'
            }

    except Exception as e:
        print('mqtt_subscribe', e)
    return result

@app.delete('/mqtt/subscribe', tags=['mqtt'])
def stop_mqtt_subscribe():
    global status_task_subscribe
    result = False
    try:
        TestMQTT.stop_subscribe()

    except Exception as e:
        print('stop_mqtt_subscribe', e)
    return result

###################################
#   サブスクリプション管理
###################################
@app.post('/subscription', tags=['manager'])
def set_subscription(usecase: str, apiname: str, endpoint: str):
    result = False
    try:
        obj = OrionSubscription(usecase, apiname)
        result = obj.set_subscription(endpoint)

    except Exception as e:
        print('set_subscription', e)
    return result

@app.get('/subscription/apiname', tags=['manager'])
def get_subscription_list(apiname: str):
    result = False
    try:
        obj = OrionSubscription(None, apiname)
        result = obj.get_subscription_apiname_list()

    except Exception as e:
        print('search_subscription', e)
    return result

@app.get('/subscription/usecase', tags=['manager'])
def get_subscription_usecase_list(usecase: str, fiware_service: str):
    result = False
    try:
        obj = OrionSubscription(usecase, None)
        result = obj.get_subscription_usecase_list(fiware_service)

    except Exception as e:
        print('get_subscription_usecase_list', e)
    return result

@app.get('/subscription', tags=['manager'])
def search_subscription(usecase: str, apiname: str):
    result = False
    try:
        obj = OrionSubscription(usecase, apiname)
        result = obj.search_subscription()

    except Exception as e:
        print('search_subscription', e)
    return result

@app.delete('/subscription', tags=['manager'])
def delete_subscription(apiname: str, subscription_id: str):
    result = False
    try:
        obj = OrionSubscription(None, apiname)
        result = obj.delete_subscription(subscription_id)

    except Exception as e:
        print('delete_subscription', e)
    return result

###################################
#   履歴データ
###################################

@app.get('/history/data', tags=['history'])
def get_history_data(apiname: str):
    result = None
    try:
        obj = History(apiname)
        result = obj.get_data()

    except Exception as e:
        print('get_history_data', e)
    
    return result

###################################
#   マップデータ
###################################
def task_convert_shapefile_to_tile(name, organ_code, tmpdir, zip_path):
    try:
        print('task_convert_shapefile_to_tile called')
        obj = Map(name, organ_code)
        obj.parse_shapefile(tmpdir, zip_path)
    
    except Exception as e:
        print('task_convert_shapefile_to_tile', e)
    
    print('task_convert_shapefile_to_tile DONE')

@app.post('/geospatial/shapefile', tags=['geospatial'])
def convert_shapefile_to_tile(name: str, organ_code: str, background_tasks: BackgroundTasks, shapefile: UploadFile=File(...)):
    result = None
    try:
        print('convert_shapefile_to_tile called')
        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, shapefile.filename)

        with open(zip_path, 'wb') as buffer:
            shutil.copyfileobj(shapefile.file, buffer)
        
        print('call background task')
        task_convert_shapefile_to_tile(name, organ_code, tmpdir, zip_path)
        #background_tasks.add_task(task_convert_shapefile_to_tile, name, organ_code, tmpdir, zip_path)
        result = {
            'status': True,
            'message': 'shapefileのタイル化処理を開始しました'
        }

    except Exception as e:
        print('convert_shapefile_to_tile', e)
    return result

def task_convert_geojson_to_tile(name, organ_code, geojson_path):
    try:
        obj = Map(name, organ_code)
        obj.convert_geojson(geojson_path)
    
    except Exception as e:
        print('task_convert_geojson_to_tile', e)

@app.post('/geospatial/geojson', tags=['geospatial'])
def convert_geojson_to_tile(name: str, organ_code: str, background_tasks: BackgroundTasks, geojson: UploadFile=File(...)):
    result = None
    try:
        tmpdir = tempfile.mkdtemp()
        geojson_path = os.path.join(tmpdir, geojson.filename)

        with open(geojson_path, 'wb') as buffer:
            shutil.copyfileobj(geojson.file, buffer)

        background_tasks.add_task(task_convert_geojson_to_tile, name, organ_code, geojson_path)
        result = {
            'status': True,
            'message': 'GeoJSONのタイル化処理を開始しました'
        }

    except Exception as e:
        print('convert_geojson_to_tile', e)
    return result

###################################
#   画面
###################################
@app.get('/ngsi', response_class=HTMLResponse, tags=['page'])
def ngsi_page(request: Request):

    return templates.TemplateResponse(
        'ngsi.html',
        {
            'request': request
        }
    )

@app.get('/', response_class=HTMLResponse, tags=['page'])
def top_page(request: Request):

    return templates.TemplateResponse(
        'top_page.html',
        {
            'request': request
        }
    )


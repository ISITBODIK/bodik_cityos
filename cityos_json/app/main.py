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
from tempfile import NamedTemporaryFile
import requests

import json
import csv
import time

import env
from env import use_kong

import myes
from myorion import MyOrion
from history import History

from myconfig import MyConfig
from configFile import configFile
from myapi import MyAPI
from uploads import MyUploadFiles
from keycloak import myKeycloak

tags_metadata = [
    {
        "name": "auth",
        "description": "認証管理"
    },
    {
        "name": "myapi",
        "description": "MyAPI管理"
    },
    {
        "name": "orion",
        "description": "Orion"
    },
    {
        "name": "history",
        "description": "履歴データ管理"
    },
    {
        "name": "uploads",
        "description": "アップロード管理"
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
    #root_path = '/webapp',
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

    return tmp_path

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
#   認証管理
###################################
class LoginRequrst(BaseModel):
    username: str
    password: str

class RefreshRequrst(BaseModel):
    refresh_token: str

@app.post('/auth/login', tags=['auth'])
def login_orion(req: LoginRequrst):
    result = None
    try:
        print('login', req)
        obj = myKeycloak()
        result = obj.login_orion(dict(req))

    except Exception as e:
        print('login_orion', e)
    return result

@app.post('/auth/refresh', tags=['auth'])
def refresh_orion(req: RefreshRequrst):
    result = None
    try:
        obj = myKeycloak()
        result = obj.refresh_orion(dict(req))
        
    except Exception as e:
        print('refresh_orion', e)
    return result

@app.post('/auth/demo/login/{apiname}', tags=['auth'])
def login_orion_demo(apiname: str):
    result = None
    try:
        obj = myKeycloak()
        result = obj.login_orion_demo(apiname)

    except Exception as e:
        print('login_orion_demo', e)
    return result


###################################
#   データモデル管理
###################################
@app.get('/myapi/public', tags=['myapi'])
def search_myapi_public(isLocation: Optional[ bool ] = False):
    result = False
    try:
        result = MyConfig.search_public_api(isLocation)
    
    except Exception as e:
        print('search_myapi_public', e)
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

###################################
#   Orionデータ
###################################
@app.post('/json', tags=['history'])
def get_orion_data(params: dict):
    result = None
    try:
        obj = MyOrion()
        result = obj.search(params)

    except Exception as e:
        print('get_orion_data', e)
    return result

@app.post('/json/protected', tags=['history'])
def get_protected_orion_data(params: dict):
    result = None
    try:
        obj = MyOrion()
        result = obj.search(params)

    except Exception as e:
        print('get_protected_orion_data', e)
    return result

###################################
#   履歴データ
###################################
@app.delete('/history', tags=['history'])
def delete_history_data(apiname: str):
    result = None
    try:
        obj = MyConfig()
        myconfig = obj.get_config(apiname)
        qs = {
            'query': {
                'match_all': {}
            }
        }
        myes.delete_document(myconfig, qs)

    except Exception as e:
        print('delete_history_data', e)
    return result

@app.post('/history', tags=['history'])
def get_history_data(params: dict):
    result = None
    try:
        obj = History()
        result = obj.search(params)

    except Exception as e:
        print('get_history_data', e)
    return result

@app.post('/history/protected', tags=['history'])
def get_protected_history_data(params: dict):
    result = None
    try:
        obj = History()
        result = obj.search(params)

    except Exception as e:
        print('get_protected_history_data', e)
    return result

###################################
#   アップロード
###################################

@app.post('/uploads', tags=['uploads'])
def upload_file(entity_type: str = Form(...), device_id: str = Form(...), upload_file: UploadFile = File(...)):
    result = None
    try:
        print('uploads', entity_type, device_id)
        obj = MyUploadFiles(entity_type)
        result = obj.save_file(device_id, upload_file)

    except Exception as e:
        print('upload_file', e)
    return result

@app.get('/uploads/{entity_type}/{device_id}', tags=['uploads'])
def get_uploaded_file(entity_type: str, device_id: str):
    result = None
    try:
        obj = MyUploadFiles(entity_type)
        streaming = obj.get_file(device_id)
        if streaming is not None:
            result = streaming

    except Exception as e:
        print('get_uploaded_file', e)
    return result

@app.get('/download/{entity_type}/{device_id}', tags=['uploads'])
def download_uploaded_file(entity_type: str, device_id: str):
    result = None
    try:
        obj = MyConfig()
        myconfig = obj.get_entity_config(entity_type)
        if myconfig['Fiware-ServicePath'].startswith('/public'):
            obj = MyUploadFiles(entity_type)
            streaming = obj.get_file(device_id)
            if streaming is not None:
                result = streaming
        else:
            print('public only')
            
    except Exception as e:
        print('download_uploaded_file', e)
    return result

###################################
#   画面
###################################
@app.get('/ngsi', response_class=HTMLResponse, tags=['page'])
def ngsi_page(request: Request):

    return templates.TemplateResponse(
        'ngsi.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/forest', response_class=HTMLResponse, tags=['page'])
def forest_page(request: Request):

    return templates.TemplateResponse(
        'forest.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/municipality', response_class=HTMLResponse, tags=['page'])
def municipality_page(request: Request):

    return templates.TemplateResponse(
        'municipality.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/elementary', response_class=HTMLResponse, tags=['page'])
def elementary_page(request: Request):

    return templates.TemplateResponse(
        'elementary.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/photo', response_class=HTMLResponse, tags=['page'])
def photo_page(request: Request):

    return templates.TemplateResponse(
        'photo.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/opendatamap', response_class=HTMLResponse, tags=['page'])
def opendatamap_page(request: Request):

    return templates.TemplateResponse(
        'opendatamap.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/dataviewer', response_class=HTMLResponse, tags=['page'])
def dataviewer_page(request: Request):

    return templates.TemplateResponse(
        'dataviewer.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/historyviewer', response_class=HTMLResponse, tags=['page'])
def dataviewer_page(request: Request):

    return templates.TemplateResponse(
        'historyviewer.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

@app.get('/mydocs', response_class=HTMLResponse, tags=['page'])
def mydocs_page(request: Request):

    return templates.TemplateResponse(
        'mydocs.html',
        {
            'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )

"""
@app.get('/ngsi', response_class=HTMLResponse, tags=['page'])
def ngsi_page(request: Request):

    return templates.TemplateResponse(
        'ngsi.html',
        {
            #'base_url': '/webapp/' if use_kong else '',
            'request': request
        }
    )
"""

@app.get('/', response_class=HTMLResponse, tags=['page'])
def top_page(request: Request):

    return templates.TemplateResponse(
        'top_page.html',
        {
            'request': request
        }
    )


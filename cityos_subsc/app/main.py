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

import datetime
import pytz
import json
import csv
import time

import queue
import env

from worker import Worker

from orion_subscription import OrionSubscription

from myconfig import MyConfig
from configFile import configFile

tags_metadata = [
    {
        "name": "myapi",
        "description": "データモデル管理"
    },
    {
        "name": "subscription",
        "description": "サブスクリプション"
    },
    {
        "name": "manager",
        "description": "サブスクリプション管理"
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
#   データモデル管理
###################################
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
#   サブスクリプション
###################################
job_queue = None
worker = None
accept_subscription = True

@app.post('/notify/{usecase}', tags=['subscription'])
def notify_subscription(usecase: str, data: dict):
    global job_queue, worker, accept_subscription
    result = False
    try:
        if accept_subscription:
            print('subscribe received', data)
            if job_queue is None:
                print('create queue')
                job_queue = queue.Queue()
            
            if worker is None:
                print('create worker')
                worker = Worker(job_queue)
                worker.start()

            info = {
                'usecase': usecase,
                'data': data
            }
            job_queue.put(info)
            result = True
        else:
            print('now subscription temporarily disabled...')        

    except Exception as e:
        print('notify_subscription', e)
    return result

@app.post('/subscription/stop', tags=['subscription'])
def stop_subscription():
    global job_queue, worker, accept_subscription
    result = False
    try:
        accept_subscription = False
        if worker is not None:
            job_queue.put(None)
            worker.join()   # 完全に終了するまで待つ
            print('workerが停止しました')
            worker = None
        result = True

    except Exception as e:
        print('stop_subscription', e)
    return result

@app.post('/subscription/restart', tags=['subscription'])
def restart_subscription():
    global accept_subscription
    result = False
    try:
        accept_subscription = True
        result = True

    except Exception as e:
        print('restart_subscription', e)
    return result

@app.get('/subscription/status', tags=['subscription'])
def check_subscription():
    global job_queue, worker, accept_subscription
    result = False
    try:
        if accept_subscription:
            result = {
                'status': 'subscription active.'
            }
            queue_status = 'OK'
            if job_queue is None:
                queue_status = 'waiting...'
            result['queue'] = queue_status

            worker_status = 'OK'
            if worker is None:
                worker_status = 'waiting...'
            result['worker'] = worker_status
        else:
            result = {
                'status': 'subscription temporalily disbled.'
            }

    except Exception as e:
        print('check_subscription', e)
    return result

###################################
#   サブスクリプション管理
###################################
@app.post('/subscription', tags=['manager'])
def set_subscription(apiname: str, usecase: str = 'history', endpoint: str = 'http://172.29.0.100:8080/notify'):
    result = False
    try:
        obj = OrionSubscription(usecase, apiname)
        url = f'{endpoint}/{usecase}'
        result = obj.set_subscription(url)

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
def get_subscription_usecase_list(fiware_service: str, usecase: str = 'history'):
    result = False
    try:
        obj = OrionSubscription(usecase, None)
        result = obj.get_subscription_usecase_list(fiware_service)

    except Exception as e:
        print('get_subscription_usecase_list', e)
    return result

@app.get('/subscription', tags=['manager'])
def search_subscription(apiname: str, usecase: str = 'history'):
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
#   画面
###################################

@app.get('/', response_class=HTMLResponse, tags=['page'])
def top_page(request: Request):

    return templates.TemplateResponse(
        'top_page.html',
        {
            'request': request
        }
    )


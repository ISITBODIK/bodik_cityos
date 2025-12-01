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
from threading import Thread

import datetime
import pytz
import json
import csv
import time

import queue
import env

from worker import Worker

tags_metadata = [
    {
        "name": "myapi",
        "description": "データモデル管理"
    },
    {
        "name": "subscribe",
        "description": "サブスクライブ"
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
#   自動実行
###################################
@app.on_event('startup')
def auto_start():
    try:
        start_subscribe_worker()

    except Exception as e:
        print('auto_start', e)

###################################
#   サブスクライブ
###################################
status_task_subscribe = False
subscribe_worker = None

def start_subscribe_worker():
    global status_task_subscribe, subscribe_worker
    result = False
    try:
        if not status_task_subscribe:
            subscribe_worker = Worker()
            if subscribe_worker is not None:
                subscribe_worker.start_subscriber()
                status_task_subscribe = True
                result = True
            else:
                print('サブスクライブワーカーを開始できませんでした')

    except Exception as e:
        print('start_subscribe_worker', e)
    
    return result

def stop_subscribe_worker():
    global status_task_subscribe, subscribe_worker
    result = False
    try:
        if status_task_subscribe and subscribe_worker is not None:
            subscribe_worker.stop_subscriber()
            subscribe_worker = None
            status_task_subscribe = False
            result = True
        else:
            print('サブスクライブしていません')

    except Exception as e:
        print('stop_subscribe_worker', e)
    
    return result


@app.get('/subscriber/stop', tags=['subscribe'])
def stop_subscriber():
    result = None
    try:
        result = stop_subscribe_worker()
        
    except Exception as e:
        print('stop_subscriber', e)
    return result

@app.post('/subscribe/start', tags=['subscribe'])
def start_subscrbe():
    result = False
    try:
        result = start_subscribe_worker()

    except Exception as e:
        print('start_subscrbe', e)

    return result

@app.get('/subscriber/status', tags=['subscribe'])
def subscriber_status():
    global status_task_subscribe
    result = None
    try:
        if status_task_subscribe:
            result = {
                'status': True,
                'message': '実行中です'
            }
        else:
            result = {
                'status': False,
                'message': '停止しています'
            }

    except Exception as e:
        print('subscriber_status', e)
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


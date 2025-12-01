import datetime
from pathlib import Path
import io
import mimetypes

from myconfig import MyConfig
import myes
import env
from env import cityos_server, s3_endpoint, s3_access_key, s3_secret_key

import boto3
from botocore.exceptions import ClientError
from fastapi.responses import StreamingResponse

class MyUploadFiles:

    PUBLIC_BUCKET = 'public'
    PROTECTED_BUCKET = 'protected'

    config = {
        'index': 'uploads',
        "mapping": {
            "mappings": {
                "properties": {
                    "entity_type": { "type": "keyword" },
                    "device_id": { "type": "keyword" },
                    "filepath": { "type": "keyword" }
                }
            }
        }
    }

    def __init__(self, entity_type):
        try:
            # entity_typeからバケットを特定する
            self.entity_type = entity_type
            obj = MyConfig()
            myconfig = obj.get_entity_config(entity_type)
            fiware_servicepath = myconfig['Fiware-ServicePath']
            if fiware_servicepath.startswith('/protected'):
                self.bucket_name = self.PROTECTED_BUCKET
            else:
                self.bucket_name = self.PUBLIC_BUCKET

            self.s3 = boto3.client(
                's3',
                endpoint_url=s3_endpoint,
                aws_access_key_id=s3_access_key,
                aws_secret_access_key=s3_secret_key
            )

            delta = datetime.timedelta(hours=9)
            self.JST = datetime.timezone(delta, 'JST')

            self.init_index()

        except Exception as e:
            print('Uploads.init', e)

    def init_index(self):
        try:
            if myes.exists(self.config) == False:
                myes.create_index(self.config)
                myes.update_index_setting(self.config)

        except Exception as e:
            print('ERROR init_index', e)

    def save_file(self, device_id, file):
        result = None
        try:
            # ファイルをS3ストレージに格納する
            myfolder = f'{self.entity_type}/{device_id}'
            file_path = f'{myfolder}/{file.filename}'
            file_url = f'{cityos_server}/uploads/{myfolder}'

            guessed, _ = mimetypes.guess_type(file.filename)
            content_type = guessed or "application/octet-stream"
            print(file_path, content_type)

            self.s3.upload_fileobj(
                file.file,
                self.bucket_name,
                file_path,
                ExtraArgs={"ContentType": content_type }
            )
            print('s3.upload_fileobj OK')

            doc_id = f'{self.entity_type}/{device_id}'
            source = myes.get_source(self.config, doc_id)
            if source is None:
                # create
                doc = {
                    'entity_type': self.entity_type,
                    'device_id': device_id,
                    'filepath': file_path
                }
                myes.create_document(self.config, doc_id, doc)
            else:
                # update
                update_doc = {
                    'doc': {
                        'filepath': file_path
                    }
                }
                myes.update_document(self.config, doc_id, update_doc)
            
            print('file_path', file_path)
            result = file_url
        
        except Exception as e:
            print('save_file', e)
        return result
    
    def get_file(self, device_id):
        result = None
        try:
            doc_id = f'{self.entity_type}/{device_id}'
            print('doc_id', doc_id)
            source = myes.get_source(self.config, doc_id)
            if source is not None:
                print('source', source)
                file_path = source['filepath']

                # --- ContentType を S3 から取得 ---
                meta = self.s3.head_object(Bucket=self.bucket_name, Key=file_path)
                content_type = meta.get("ContentType")
                if not content_type:  # S3 に無い場合は拡張子から推測
                    guessed, _ = mimetypes.guess_type(file_path)
                    content_type = guessed or "application/octet-stream"

                fileobj = io.BytesIO()
                self.s3.download_fileobj(self.bucket_name, file_path, fileobj)
                fileobj.seek(0)
                result = StreamingResponse(fileobj, media_type=content_type)
        
        except Exception as e:
            print('get_file', e)
        return result
    
import shutil
from pathlib import Path

import myes
import env
from env import cityos_server

UPLOAD_FOLDER = Path('./uploads')

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

    def __init_(self):
        try:
            if not UPLOAD_FOLDER.exists():
                UPLOAD_FOLDER.mkdir()

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

    def save_file(self, entity_type, device_id, file):
        result = None
        try:
            myfolder = f'{UPLOAD_FOLDER}/{entity_type}/{device_id}'
            Path(myfolder).mkdir(parents=True, exist_ok=True)
            file_url = f'{cityos_server}/{myfolder}'

            file_path = f'{myfolder}/{file.filename}'
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            doc_id = f'{entity_type}/{device_id}'
            source = myes.get_source(self.config, doc_id)
            if source is None:
                # create
                doc = {
                    'entity_type': entity_type,
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
    
    def get_file(self, entity_type, device_id):
        result = None
        try:
            doc_id = f'{entity_type}/{device_id}'
            print('doc_id', doc_id)
            source = myes.get_source(self.config, doc_id)
            if source is not None:
                result = source['filepath']
        
        except Exception as e:
            print('get_file', e)
        return result
    
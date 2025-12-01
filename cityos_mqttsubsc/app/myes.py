import json
from elasticsearch import Elasticsearch, helpers

from env import es_server

############################
#   インデックス
############################
def exists(config):

    es = None

    result = False

    try:
        es = Elasticsearch(es_server)
        result = es.indices.exists(index=config['index'])
    
    except Exception as e:
        print('index exists', e)

    finally:
        if es is not None:
            es.close()

    return result

def create_index(config):
    
    es = None

    try:
        es = Elasticsearch(es_server)
        if not es.indices.exists(index=config['index']):
            es.indices.create(index=config['index'], body=config['mapping'])

    except Exception as e:
        print('create_index ERROR:', e)

    finally:
        if es is not None:
            es.close()

def update_index_setting(config):
    es = None
    result = False
    try:
        es = Elasticsearch(es_server)
        if es.indices.exists(index=config['index']):
            es.indices.put_settings(index=config['index'], body={ "index.mapping.total_fields.limit": 20000 })
            result = True

    except Exception as e:
        print('create_index ERROR:', e)

    finally:
        if es is not None:
            es.close()

def delete_index(config):
    
    es = None

    try:
        es = Elasticsearch(es_server)
        es.indices.delete(index=config['index'])

    except Exception as e:
        print('delete_index ERROR:', e)

    finally:
        if es is not None:
            es.close()

def list_index():

    index_list = None

    es = None
    try:
        es = Elasticsearch(es_server)
        index_list = es.indices.get('*')

    except Exception as e:
        print('list_index ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return index_list


############################
#   ドキュメント
############################
def create_document(config, doc_id, doc, refresh = False):

    result = {}

    try:
        es = Elasticsearch(es_server)
        es.create(index=config['index'], id=doc_id, body=doc, refresh=refresh)
        result['status'] = 'OK'

    except Exception as e:
        print('create_document ERROR:', str(e))
        result['status'] = 'exception'
        result['error'] = str(e)

    finally:
        if es is not None:
            es.close()

    return result


def es_open():
    es = Elasticsearch(es_server)
    return es

def es_create_document(es, config, doc_id, doc):
    es.create(index=config['index'], id=doc_id, body=doc)
    return

def es_close(es):
    if es is not None:
        es.close()
    return

def create_documents(config, list_doc):

    count = 0

    try:
        es = Elasticsearch(es_server)
        for obj in list_doc:
            try:
                es.create(index=config['index'], id=obj['doc_id'], body=obj['doc'])
                count += 1

            except Exception:
                pass

    except Exception as e:
        print('create_documents ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return count


def delete_document(config, q):

    es = None

    try:
        es = Elasticsearch(es_server)
        es.delete_by_query(index=config['index'], body=q, wait_for_completion=True)

    except Exception as e:
        print('delete_document ERROR:', e)

    finally:
        if es is not None:
            es.close()


def delete_document_id(config, doc_id):

    es = None

    try:
        es = Elasticsearch(es_server)
        es.delete(index=config['index'], id=doc_id)

    except Exception as e:
        print('delete_document ERROR:', e)

    finally:
        if es is not None:
            es.close()


# データ件数が１万件を超える場合、スクロールが必要
def search_document(config, q):

    result = []
    es = None
    sid = None
    try:
        es = Elasticsearch(es_server)
        page = es.search(index=config['index'], body=q, size=1000, scroll='1m')
        if page:
            sid = page['_scroll_id']
            scroll_size = len(page['hits']['hits'])

            while scroll_size > 0:
                for obj in page['hits']['hits']:
                    result.append(obj['_source'])

                # 次のページを取得
                page = es.scroll(scroll_id=sid, scroll='1m')
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

    except Exception as e:
        print(config['index'], 'search_document ERROR:', e)

    finally:
        if es is not None:
            if sid is not None:
                es.clear_scroll(scroll_id=sid)

            es.close()

    return result


def get_source(config, doc_id):
    response = None
    es = None
    try:
        es = Elasticsearch(es_server)
        response = es.get_source(index=config['index'], id=doc_id)

    except Exception as e:
        pass
        #print('get_source ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return response


def count_document(config):

    count = 0

    es = None

    try:
        es = Elasticsearch(es_server)

        result = es.count(index=config['index'])
        count = result['count']

    except Exception as e:
        print(config['index'], 'count_document ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return count

def count_documentByQ(config, q):

    count = 0

    es = None

    try:
        es = Elasticsearch(es_server)

        result = es.count(index=config['index'], body=q)
        if result:
            count = result['count']

    except Exception as e:
        print(config['index'], 'count_documentByQ ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return count

def update_document(config, doc_id, doc):

    result = False

    try:
        es = Elasticsearch(es_server)
        
        es.update(index=config['index'], id=doc_id, refresh='wait_for', body=doc)
        result = True

    except Exception as e:
        print('update_document ERROR:', e)

    finally:
        if es is not None:
            es.close()

    return result


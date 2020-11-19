import boto3
import json
import os
from pprint import pprint
import yaml
import json
import logging
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def filter_cre_id(cre_file, cre_id):
    """filter_cre_id returns all items linked to the specific cre_id
    path: /cre/{id}"""
    res = []
    cres = ""
    cre_file = yaml.safe_load(cre_file)   
    for cre in cre_file:
        if cre_id == cre.get('CRE-ID-lookup-from-taxonomy-table'):
            res.append(cre)
    return res


def filter_all(cre_file):
    """filter_all returns all cres along with their links in the file specified
    path: /cre"""
    res = []
    cres = ""
    cre_file = yaml.safe_load(cre_file)   
    for cre in cre_file:
        res.append(cre)
    return res

    
def filter_link_is_mentioned_in_cres(cre_file, link_tag, link_value):
    """filter_link_is_mentioned_in_cres all cres that the link appears in
    path: /link?tag=x&value=y
     """
    res = []
    cres = ""
    cre_file = yaml.safe_load(cre_file)   
    for cre in cre_file:
        theset = set(k.lower() for k in cre)
        if link_tag.lower() in theset:
            for k, v in cre.items():
                if k.lower() == link_tag.lower() and cre[k] == link_value:
                    res.append(cre)
    return res


def cre_to_json_str(cre):
    res = json.dumps(cre)
    logger.info(res)
    return res or ""

def list_files(bucket):
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=bucket)
    return objects


def get_file(bucket, file_obj):
    s3_res = boto3.resource('s3')
    return s3_res.Object(bucket, file_obj['Key']).get()['Body'].read().decode()

# TODO:
# * create testing events
# * create error handling method
# * create local e2e testing script
# * add paths and query string and auth to template.yaml
def lambda_handler(event, context):
    ret = {
             'statusCode': 200,
             'body':"foo",
         }
    cres = []
    query_str = event.get("queryStringParameters")
    path_params = event.get('pathParameters')
    logger.debug("called with query_str %s"%query_str)
    logger.debug("called with path_params ")
    logger.debug(path_params)

    if path_params:
        if "cre_id" in path_params and path_params["cre_id"] != "":
            #filter by cre_id
            logger.debug("filtering by cre_id")
            cres.extend([filter_cre_id(cre_file) for cre_file in s3_file_generator()])
        elif "link" in path_params:
            logger.debug("filtering by link")
            link_tag = query_str.get('tag', None)
            link_value = query_str.get('val', None)    
            cres.extend([filter_link_is_mentioned_in_cres(cre_file,link_tag,link_value) for cre_file in s3_file_generator()])    
            pass #filter by link
        elif "cres" in path_params:
            #get all
            logger.debug("getting everything")
            cres.extend([filter_all(cre_file) for cre_file in s3_file_generator()])
    else:
        logger.debug("error")
        error("this seems to have been misconfigured")

    logger.info(cre_to_json_str(cres))
    # ret['body']['cres'] = cre_to_json_str(cres)
        
    return ret

def error(message):
    pass

def s3_file_generator():
    bucket = os.environ.get("BUCKET_NAME")
    objects = list_files(bucket)
    for file_obj in objects.get('Contents'):
        obj = []
        cre_file = get_file(bucket, file_obj)
        yield cre_file
        
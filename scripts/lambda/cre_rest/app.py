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
    cre_list = yaml.safe_load(cre_file)
    if type(cre_list) != list:
        return res

    for cre in cre_list:
        if cre_id == cre.get('CRE-ID-lookup-from-taxonomy-table'):
            res.append(cre)
    return res


def filter_all(cre_file):
    """filter_all returns all cres along with their links in the file specified
    path: /cre"""
    res = []
    cres = ""
    cre_file = yaml.safe_load(cre_file)
    if cre_file == "keep":
        return res
    for cre in cre_file:
        res.append(cre)
    return res

    
def filter_link_is_mentioned_in_cres(cre_file, link_tag, link_value):
    """filter_link_is_mentioned_in_cres all cres that the link appears in
    path: /link?tag=x&value=y
     """
    res = []
    cre_yaml = yaml.safe_load(cre_file)   
    for cre in cre_yaml:
        theset = set(k.lower() for k in cre)
        if link_tag.lower() in theset:
            for k, v in cre.items():
                if k.lower() == link_tag.lower() and str(v) == str(link_value):
                    res.append(cre)
    return res


def cre_to_json_str(cre):
    res = json.dumps(cre)
    return res or ""

def list_files(bucket):
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=bucket)
    return objects


def get_file(bucket, file_obj):
    s3_res = boto3.resource('s3')
    return s3_res.Object(bucket, file_obj['Key']).get()['Body'].read().decode()


def lambda_handler(event, context):
    ret = {
             'statusCode': 200,
             'body':"foo",
         }
    cres = []
    path = event.get('path')
    query_str = event.get("queryStringParameters")
    path_params = event.get("pathParameters")
    logger.debug("called with query_str %s"%query_str)
    logger.debug("called with path_params ")
    logger.debug(event.get("pathParameters"))

    
    if "cre" in path and path_params and path_params.get("id"):
            #filter by cre_id
            cre_id = path_params["id"]
            logger.debug("filtering by cre_id %s"%cre_id)
            cres.extend([filter_cre_id(cre_file,cre_id) for cre_file in s3_file_generator()])
    elif "link" in path and 'tag' in query_str and 'val' in query_str:
            logger.debug("filtering by link")
            link_tag = query_str.get('tag', None)
            link_value = query_str.get('val', None)    
            cres.extend([filter_link_is_mentioned_in_cres(cre_file,link_tag,link_value) for cre_file in s3_file_generator()])    
            pass #filter by link
    elif "cres" in path:
            #get all
            logger.debug("getting everything")
            cres.extend([filter_all(cre_file) for cre_file in s3_file_generator()])
    else:
        logger.debug("error")
        error("this seems to have been misconfigured")

    # logger.info(cre_to_json_str(cres))
    ret['body'] = {}
    ret['body'] = cre_to_json_str(cres)
        
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
        
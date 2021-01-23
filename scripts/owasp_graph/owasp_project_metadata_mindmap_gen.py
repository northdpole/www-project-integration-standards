import requests
import pydot
import os
import yaml
import sys
import base64
import time
import argparse
import json
import re
import github3
from collections import namedtuple
from pprint import pprint
from random import randint
# from github3 import GitHub
from urllib.parse import urlparse
from itertools import chain

session = requests.Session()

class Info:
    def __init__(self, name='Unnamed Project',
                       repository=None,
                       tags=[],
                       sdlc=[],
                       example_usage='',
                       output_type='',
                       level = 0,
                       type='',
                       pitch = '',
                       audience='',
                       social=''):
        self.name = name
        self.repository = repository
        self.tags = tags
        self.sdlc = sdlc
        self.example_usage = example_usage
        self.output_type = output_type

        self.level = ''
        self.type = ''
        self.pitch = ''

        self.audience = ''
        self.social = ''


    def __repr__(self):
        return yaml.dump(vars(self))


def add(graph, root, child):
    edge = pydot.Edge(root,child)
    graph.add_edge(edge)


def extract_index_meta(index:str):
    regexp = {'title': '(title: (?P<title>.+))',
                'tags':'(tags: (?P<tags>.+))',
                'level':'(level: (?P<level>.+))',
               'type':'(type: (?P<type>.+))',
                'pitch':' (pitch: (?P<pitch>.+))'}
    results = {}
    metadata = re.search("---.*---",index,re.DOTALL)
    title = tags = level = type = pitch = ""
    if metadata is not None:
        for k,v in regexp.items():
            m = re.search(v,metadata.group())
            if m is not None:
                results[k] = m.group(k).strip()
            else:
                results[k] = ''
        return (results['title'],
                results['tags'],
                results['level'],
                results['type'],
                results['pitch'])
    else:
        print('failed to match header')
    print("regexp bug, could not parse "+index)
    return (None,None,None,None,None)

def extract_info_meta(info:str):
    # TODO: parse info.md which is unstructured html/markdown
    return None, None, None

def get_project_meta(project_url:str):
    """ parse:
    * index.md for the string between the "---" tags in order to extract title, tags, level, type and pitch
    * info.md to extract audience, social links and code repo\
    args: project_url github url to a project
    """
    if project_url.endswith(".md"):
        print("Bug")
    if not project_url.endswith("/"):
        project_url = project_url + "/"
        print("added trailing slash")

    index_url = project_url + "index.md"
    index_file = session.get(index_url).json()
    index_content = base64.b64decode(index_file['content']).decode('utf-8')
    title, tags, level, type, pitch = extract_index_meta(index_content)

    
    info_url = project_url + "info.md"
    info_file = session.get(info_url).json()
    info_content = base64.b64decode(index_file['content']).decode('utf-8')
    audience, social, code= extract_info_meta(info_content)
    
    project_info = Info(name=title,
                        repository=code,
                        tags=tags,
                        level=level,
                        type=type,
                        pitch=pitch,
                        audience=audience,
                        social=social)
    return project_info

def gather_metadata(reponame: str, orgname: str) -> list:
    """Builds the repo object for every repo in the org
    :param reponame if not None, it will search only for the specific repo
    :param orgname if not None, it will search only for the specific org
    :returns list of dicts representing the info.yaml files
    """
    print("gathering metadata for "+orgname)
    result = []
    connection = github3.GitHub()

    query = 'filename:"info.md" path:/'
    if reponame is not None:
        search = f"repo:{reponame} {query}"
    elif orgname is not None:
        search = f"org:{orgname} {query}"
    metadata = connection.search_code(search)

    for f in metadata:
        time.sleep(5) # throttle locally so github doesn't complain
        content = session.get(f.url)
        print("processing: "+f.url)
        if content.status_code == 200:
            resp = json.loads(content.text)
            print(f"analysing data for {resp['_links']['html']}")
            
            if "chapter" in resp['_links']['html'].lower(): # skip chapter pages
                print(resp['_links']['html'].lower()+" is a chapter, skipping for now")
                continue

            # extract project base so we can get both index and info 
            project_base = re.sub(r'\?ref=.*',"",resp['url']).replace("info.md","")
            result.append(get_project_meta(project_base))
        else:
            print(f"ERROR response code: {content.status_code}")
    return result

def metadata(reponame: str, orgname: str,metadata: dict) -> dict:
    """ searches for info.yaml in the repo or the org defined
        finds the info.yaml metadata files and fetches them
        returns object representation of metadata files groupped by sdlc step
    """
    data = gather_metadata(reponame=reponame,orgname=orgname)
    for pinfo in data:

        if pinfo.sdlc == []: # handle case where people haven't updated their sdlc steps
            pinfo.sdlc == ['General']
        for step in pinfo.sdlc:
            if step not in metadata:
                metadata[step] = list()
            metadata[step].append(pinfo)
    return metadata

def build_metadata(org_dict: dict, repo_dict: dict) -> list:
    mindmap = {"General":[], "Planning":[],"Analysis":[],"Design":[],"Implementation":[],"Maintenance":[],"Strategy":[],"Culture":[]}

    for human_org_name, github_org_name in org_dict.items():
        print("Processing %s:%s"%(human_org_name,github_org_name))
        mindmap = metadata(reponame=None, orgname=github_org_name, metadata=mindmap)

    # for human_repo_name,github_repo_name in repo_dict.items():
    #     print(f"Processing {human_repo_name}")
    #     mindmap = enhance_metadata(orgname=None,  reponame=github_repo_name,metadata=mindmap)
    return mindmap

def build_graph(metadata: dict)->pydot.Dot:
    graph = pydot.Dot(graph_type="graph", rankdir="UD")
    for sdlc_step,projects in metadata.items():
        add(graph,"sdlc",sdlc_step)
        for project in projects:
            add(graph,sdlc_step,project.name)
    return graph



if __name__ == "__main__":

    orgs = {"owasp":"OWASP", "zap":"zap"} #{"testOrgForMetadataScript":"testOrgForMetadataScript"} this should eventually be a yaml file or some other easily parsable file mapping repos to projects
    repos = {} #{"standaloneTestRepo1":"northdpole/standaloneTestRepo1","standaloneTestRepo2":"northdpole/standaloneTestRepo2"}
    
    session.auth = (os.environ.get('GITHUB_USERNAME'), os.environ.get('GITHUB_TOKEN'))

    metadata = build_metadata(org_dict=orgs, repo_dict=repos)
    graph = build_graph(metadata)

    graph.write("map.dot")
    graph.write_png("map.png")
    os.stat("map.png")
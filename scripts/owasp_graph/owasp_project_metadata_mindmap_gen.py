import requests
import pydot
import os
import yaml
import sys
import base64
import time
import argparse
import json
from collections import namedtuple
from pprint import pprint
from random import randint
from github3 import GitHub
from urllib.parse import urlparse
from itertools import chain



class Info:
    def __init__(self, info_json: dict):
        values = info_json.get('info',info_json)
        self.name = values['name']
        self.repository = values['repository']
        self.tags = values['tags']
        self.sdlc = values['sdlc']
        self.example_usage = values['example_usage']
        self.output_type = values['output_type']
    
    def __repr__(self):
        return yaml.dump(vars(self))


def add(graph, root, child):
    edge = pydot.Edge(root,child)
    graph.add_edge(edge)

def gather_metadata(reponame: str, orgname: str) -> list:
    """Builds the repo object for every repo in the org
    :param reponame if not None, it will search only for the specific repo
    :param orgname if not None, it will search only for the specific org
    :returns list of dicts representing the info.yaml files
    """
    result = []
    connection = GitHub()
    query = "filename:info.yaml path:/"
    if reponame is not None:
        search = f"repo:{reponame} {query}"
    elif orgname is not None:
        search = f"org:{orgname} {query}"

    metadata = connection.search_code(search)

    for f in metadata:
        time.sleep(1)
        content = requests.get(f.url)
        if content.status_code == 200:
            resp = json.loads(content.text)
            print(f"analysing data for {resp['_links']['html']}")
            raw = base64.b64decode(resp['content']).decode('utf-8')
            try:
                data = yaml.safe_load_all(raw)
                for dat in data:
                    result.append(dat)
            except Exception as e:
                print(f"Could not read metadata from repo {f.url}, skipping")
                pprint(e)
                continue
            print("Success")
            
        else:
            print(f"ERROR response code: {content.status_code}")
    return result

def enhance_metadata(reponame: str, orgname: str,metadata: dict) -> dict:
    """ searches for info.yaml in the repo or the org defined
        finds the info.yaml metadata files and fetches them
        returns object representation of metadata files groupped by sdlc step
    """
    data = gather_metadata(reponame=reponame,orgname=orgname)
    for dat in data:
        info =  dat.get('info', None)
        if info:
            for step in info.get('sdlc',None):
                if step not in metadata:
                    metadata[step] = list()
                metadata[step].append(Info(dat))
    return metadata

def build_metadata(org_dict: dict, repo_dict: dict) -> list:
    mindmap = {"Planning":[],"Analysis":[],"Design":[],"Implementation":[],"Maintenance":[],"Strategy":[],"Culture":[]}

    for human_org_name,github_org_name in org_dict.items():
        print(f"Processing {human_org_name}")
        mindmap = enhance_metadata(reponame=None, orgname=github_org_name,metadata=mindmap)

    for human_repo_name,github_repo_name in repo_dict.items():
        print(f"Processing {human_repo_name}")
        mindmap = enhance_metadata(orgname=None,  reponame=github_repo_name,metadata=mindmap)
    return mindmap

def build_graph(metadata: dict)->pydot.Dot:
    graph = pydot.Dot(graph_type="graph", rankdir="UD")
    for sdlc_step,projects in metadata.items():
        add(graph,"sdlc",sdlc_step)
        for project in projects:
            add(graph,sdlc_step,project.name)
    return graph



if __name__ == "__main__":

    orgs = {"testOrgForMetadataScript":"testOrgForMetadataScript","owasp":"owasp", "zap":"zap"} # this should eventually be a yaml file or some other easily parsable file mapping repos to projects
    repos = {"standaloneTestRepo1":"northdpole/standaloneTestRepo1","standaloneTestRepo2":"northdpole/standaloneTestRepo2"}

    parser = argparse.ArgumentParser(description='SDLC Metadata extractor and graph builder for OWASP projects on GitHub')
    args = parser.parse_args()
    
    metadata = build_metadata(org_dict=orgs,repo_dict=repos)
    graph = build_graph(metadata)

    graph.write("map.dot")
    graph.write_png("map.png")
    os.stat("map.png")
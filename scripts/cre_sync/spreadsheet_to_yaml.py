import gspread
import yaml
import tempfile
import jsonschema
import json
import os.path
import logging
import git

from pprint import pprint
from datetime import datetime
from github import Github

# todo: generate schema from existing yaml, validate against schema  -- done
# commit, -- done
# issue pull request  -- done
# migrate gspread to work as a bot as well as oauth -- done
# only create a pull request if there are changes (run a git diff first?) -- done
# sync to spreadsheet (different script runs from master)
# make github action -- done
# feature: grab both link text and link value from spreadsheet -- very hard with gspread
# feature: make schema extendable, have a KEYS list representing supported standards/keywords(can be "test with, controls etc")
#  and then optionally map a cre to standards  -- done, schema is a separate file, easily extendable to recognise other standards

spreadsheets_file = "working_spreadsheets.yaml"
commit_msg_base = "cre_sync_%s" % (datetime.now().isoformat().replace(":", "."))

# gspread_creds_file = " ~/.config/gspread/credentials.json" # OAUTH default credentials location
# gspread_creds_file = "~/.config/gspread/service_account.json" # Service Account default creds location


logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CRE_LINK_schema={}

def readSpreadsheet(url: str, cres_loc: str, alias:str):
    """given remote google spreadsheet url,
     reads each workbook into a yaml file"""
    # gc = gspread.oauth() # oauth config, TODO (northdpole): make this configurable
    changes_present = False
    try:
        gc = gspread.service_account()
        sh = gc.open_by_url(url)
        logger.debug("accessing spreadsheet \"%s\" : \"%s\""%(alias,url))
        for wsh in sh.worksheets():
            if wsh.title[0].isdigit() and wsh.title == '4. foo test':
                logger.debug(
                    "handling worksheet %s  (remember, only numbered worksheets will be processed by convention)" % wsh.title)

                records = wsh.get_all_records()
                toyaml = yaml.safe_load(yaml.dump(records))

                try:
                    validateYaml(yamldoc=toyaml, schema=CRE_LINK_schema)
                    logger.debug("Worksheet is valid, saving to disk")
                    with open(os.path.join(cres_loc, wsh.title + ".yaml"), "wb") as fp:
                        fp.write(yaml.dump(toyaml, encoding='utf-8'))
                        changes_present = True
                except jsonschema.exceptions.ValidationError as ex:
                    logger.error(wsh.title + " failed validation")
                    logger.error(ex)
    except gspread.exceptions.APIError as ae:
        logger.error("Error opening spreadsheet \"%s\" : \"%s\""%(alias,url))
        logger.error(ae)
    return changes_present


def validateYaml(yamldoc: str, schema: str):
    jsonschema.validate(instance=yamldoc, schema=schema)


def create_branch(branch_name):
    g = git.Git()
    repo = git.Repo(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
    current_branch = repo.active_branch.name
    g.checkout("-b", branch_name)
    g.checkout(current_branch)


def add_to_github(cre_loc:str, alias:str,apikey):
    global commit_msg_base
    commit_msg = "%s-%s"%(commit_msg_base,alias)
    branch_name = commit_msg_base

    repo = git.Repo(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))
    g = git.Git()
    
    logger.info("Adding cre files to branch %s"% branch_name)
    current_branch = repo.active_branch.name
    try:
        g.checkout(branch_name)
        g.add(cre_loc)
        g.commit("-m", commit_msg)

        repo.remotes.origin.push(branch_name)
        remoteURL = [url for url in repo.remotes.origin.urls]        
        createPullRequest(apiToken=apikey, repo=remoteURL[0].replace("git@github.com:", "").replace(".git", ""),
                        title=commit_msg, srcBranch=commit_msg_base, targetBranch="master")
    except git.exc.GitCommandError as gce:
        # if there's an error (commonly due to no changes, skip pushing a new branch)
        logger.error("Skipping push due to git error trying to sync " + commit_msg)
        logger.error(gce)
            
    g.checkout(current_branch)



def createPullRequest(apiToken:str, repo:str, title:str, srcBranch:str, targetBranch:str="master"):
    logger.info("Issuing pull request from %s to master for repo %s" % (srcBranch, repo))
    github = Github(apiToken)
    body = "CRE Sync %s" % title
    pr = github.get_repo(repo).create_pull(title=title, body=body, head=srcBranch, base="master")


def writeSpreadsheet(local, url):
    pass


def main():
    global CRE_LINK_schema
    script_path = os.path.dirname(os.path.realpath(__file__))
    cre_loc = os.path.join(script_path, "../../cres")
    schema_loc = os.path.join(script_path,"cre_schema.json")
    with open(schema_loc,'r') as schema_file:
        CRE_LINK_schema = json.load(schema_file)

    with open(os.path.join(script_path, spreadsheets_file)) as sfile:
        create_branch(commit_msg_base)
        urls = yaml.safe_load(sfile)
        for spreadsheet_url in urls:
            logger.info("Dealing with spreadsheet %s"%spreadsheet_url['alias'])
            if readSpreadsheet(spreadsheet_url['url'], cres_loc=cre_loc,alias=spreadsheet_url['alias']):
                add_to_github(cre_loc, spreadsheet_url['alias'],os.getenv("GITHUB_API_KEY"))
            else:
                logger.info("Spreadsheet \"%s\" didn't produce any changes, no pull request needed"%spreadsheet_url['alias'])
if __name__ == "__main__":
    main()

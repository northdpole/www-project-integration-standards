import gspread
import yaml
import time
import tempfile
import jsonschema
import json
import os.path
import logging
import git
import argparse
from pprint import pprint
from datetime import datetime
from github import Github

spreadsheets_file = "working_spreadsheets.yaml"
commit_msg_base = "cre_sync_%s" % (datetime.now().isoformat().replace(":", "."))

CRE_LINK_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "CRE-ID-lookup-from-taxonomy-table": {"type": "string"},
            "CS": {"type": "string"},
            # type string handles the edge-case of empty cell
            "CWE": {"type": ["number", "string"]},
            "Description": {"type": "string"},
            "Development guide (does not exist for SessionManagement)": {"type": "string"},
            "ID-taxonomy-lookup-from-ASVS-mapping": {"type": "string"},
            "Item": {"type": "string"},
            "Name": {"type": "string"},
            "OPC": {"type": "string"},
            "Top10 (lookup)": {"type": "string"},
            "WSTG": {"type": "string"},
        },
        # "required": ["CRE-ID-lookup-from-taxonomy-table"]
    }
}
logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

  
def writeSpreadsheet(url: str, cres: list, worksheet_title:str):
    """given a yaml file writes each cre link into a remote google spreadsheet url"""
    # try:
    gc = gspread.service_account()
    sh = gc.open_by_url(url)
    # check if worksheet exists
    worksheet = None
    for wsh in sh.worksheets():
        if wsh.title == worksheet_title:
            worksheet = wsh
    # create if not exists
    if not worksheet:
        worksheet = sh.add_worksheet(title=worksheet_title, rows="1", cols="200")
        # write header
        keys = list(cres[0].keys())
        worksheet.append_row(keys)
    spreadsheet = []
    for cre in cres:
        spreadsheet.append(list(cre.values()))
    
    # batch append in a single request since limit it 40k reads or writes a day
    worksheet.append_rows(spreadsheet)

def validateYaml(yamldoc: str, schema: str):
    """asserts `yamldoc` is according to `schema` 
    throws exception if not"""
    jsonschema.validate(instance=yamldoc, schema=schema)


def read_cre(location:str)->str:
    with open(location,"r") as cfile:
        if location.endswith(".yaml"):
            cres = yaml.safe_load(cfile)
            # pprint(cres)
            try:
                validateYaml(cres,CRE_LINK_schema)
                return cres
            except jsonschema.exceptions.ValidationError as ex:
                    logger.error("File %s not valid"%location)
                    logger.errot(ex)


def main():
    script_path = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument("--cres", help="where to load cres from")
    parser.add_argument("--spreadsheet", help="where to write cres to")
    args = parser.parse_args()
    
    cre_loc = args.cres # folder to load cre files from. read from argparse
    spreadsheet_url = args.spreadsheet # where to sync the files to, read from argparse
    cre_list = []
    for root,dirs,files in os.walk(cre_loc):
        for cfile in files:
            pprint(cfile)
            cres = read_cre(location=os.path.join(root,cfile))            
            if len(cres) > 0:
                cre_list.extend(cres)
                writeSpreadsheet(spreadsheet_url,cres,cfile)
            else:
                logger.info("cres \"%s\" didn't produce any docs")

if __name__ == "__main__":
    main()

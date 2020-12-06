CRE Yaml to Spreadsheet Sync
===============================

This script when executed reads the CREs in the target directory and for each creates a tab in the spreadsheet you point it to

Assumptions
-----------
* All CREs need to follow the template defined by ```CRE_LINK_schema```, the schema has been relaxed for this script to allow for empty values in most elements.


Running
-------
* Setup gspread for you, if you want to run this script as a user you are looking for an OAUTH token, otherwise you need a Service Account: https://gspread.readthedocs.io/en/latest/oauth2.html#enable-api-access
* Install dependencies on requirements.txt
* Run:
```  python ./yaml-to-spreadsheet.py --cres <path to the dir with the yaml files you want to upload> --spreadsheet  "<google sheets url you want to sync with>"
```
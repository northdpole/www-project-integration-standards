Create Graph With OWASP Projects
===
Warning, this is highly experimental.
Main purpose is to showcase the metadata in `index.md`

This script is meant to parse a list of organisations and/or repositories which hold OWASP projects and create a mind map of them.

Usage
----

Preferably in a virtual environment

```
pip install -r requirements.txt
GITHUB_USERNAME=<your username> GITHUB_TOKEN=<your github personal access token> python owasp_project_metadata_mindmap_gen.py
```

Output is a `map.dot` and a `map.png` file.
For now these files only have basic data since most repos do not hold interesting metadata

Future Improvements
----

* Make into github action which runs on a cron schedule
* Add colours for each step of the SDLC and related items
* Make node names into links to the project
* Make interactive by creation of a github.io page with javascript that parses `map.dot` and at a minum provides usage instructions (and more info) in a sidepanel when clicking on a node.
* When projects update their index.md metadata, create a schema and validate metadata against the schema.
* Add better logging

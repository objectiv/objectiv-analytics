# Generating docs

Basically, generating and publishing the API docs for `Bach` involve a few steps:
1. Configure environment for Sphinx:
```bash
  virtualenv -p python3 venv
  . venv/bin/activate
  # install sphinx requirements
  pip install -r requirements.txt
  # install bach in edit mode
  pip install -e ../../bach
  # install objectiv_bach in edit mode
  pip install -e ../../modelhub
```

2. Generate HTML fragments:
```bash
  make clean html
```
3. Push generated docs to docusaurus:
   1. Make sure to have a checkout of objectiv/objectiv.io.
   2. Run:
```bash
   python generate.py
```

This process will generate and push the html files to docusaurus. How to run / publish the website is 
detailed in the respective readme.

---
**NOTE**

The generation script does not remove any files that were previously generated. If you rerun the script, 
either make sure you manually delete any removed files from your branch manually, or start on a clean 
branch/PR.

---

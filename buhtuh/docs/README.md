#Generating docs

Basically, generating and publishing the api docs for `buhtuh` involve a few steps:
1. Configure environment for Sphinx: setup Python environment:
   ```bash
      virtualenv -p python3 venv
      . venv/bin/activate
      pip install -r requirements.txt
2. Generate HTML fragments:
```bash
make html
```
3. Push generated docs to docusaurus:
   1. Make sure to have a checkout of objectiv/objectiv.io
   2. Run:
   ```bash
   python generate.py
   ```

This process will generate and push the html files to docusaurus. How to run / publish the website is detailed in the 
respective readme 

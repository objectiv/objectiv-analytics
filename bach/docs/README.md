# Generating docs for Bach

Generating and publishing the docs for `Bach` involve a few steps:

1. Configure the environment for Sphinx:
```bash
  virtualenv -p python3 venv
  . venv/bin/activate
  # install sphinx requirements
  pip install -r requirements.txt
  # install bach in edit mode
  pip install -e ../../bach
  # install modelhub in edit mode
  pip install -e ../../modelhub
```

2. Generate Docusaurus modeling docs:
```bash
  make clean doctest docusaurus
  # OR to also clean up the objectiv.io repo's /docs/modeling folder
  # make clean clean-target doctest docusaurus
```
3. Push generated docs to docusaurus:
   1. Make sure to have a checkout of objectiv/objectiv.io.
   2. Run:
```bash
   make copy-target
  # OR to run a fully clean build from scratch and copy it
  # make clean clean-target doctest docusaurus copy-target
```

This process will generate and push the .mdx files to the objectiv.io repo. How to run / publish the docs is 
detailed in the respective README.

---
**NOTE**

The generation script does not remove any files that were previously generated. If you rerun the script, 
either make sure you manually delete any removed files from your branch manually, start on a clean 
branch/PR, or run `make clean-target`, e.g.:
```bash
  make clean clean-target docusaurus
```

---

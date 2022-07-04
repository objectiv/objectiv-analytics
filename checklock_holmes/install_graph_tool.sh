#! /usr/bin/bash
source venv/bin/activate

touch /etc/apt/sources.list.d/graph_tool.list
echo "deb [arch=amd64] http://downloads.skewed.de/apt focal main" | tee /etc/apt/sources.list.d/graph_tool.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25
apt-get update
apt-get install build-essential
apt-get install python3-graph-tool python3-matplotlib python3-cairo

#python3-cairo from Ubuntu's repository is linked with a different python version; we need to improvise
apt purge python3-cairo
apt install libcairo2-dev pkg-config python3-dev

pip install --force-reinstall pycairo
pip install zstandard

cp -R /usr/lib/python3/dist-packages/graph_tool venv/lib/python3.8/site-packages

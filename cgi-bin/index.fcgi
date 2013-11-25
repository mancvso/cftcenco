#!/home/cftcenco/apps/cftcenco/venv/bin/python
import sys
import os

execfile('/home/cftcenco/apps/cftcenco/venv/bin/activate_this.py', dict(__file__='/home/cftcenco/apps/cftcenco/venv/bin/activate_this.py'))

sys.path.insert(0, "/home/cftcenco/apps/cftcenco/venv/lib/python2.6")
sys.path.insert(13, "/home/cftcenco/apps")
sys.path.insert(13, "/home/cftcenco/apps/cftcenco")

os.chdir("/home/cftcenco/apps/cftcenco")

#/home/cftcenco/apps/cftcenco/venv/bin/python
from flup.server.fcgi import WSGIServer
from cftcenco import app

if __name__ == '__main__':
    WSGIServer(app).run()

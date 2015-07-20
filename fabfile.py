from fabric.api import *
from fabric.contrib.project import rsync_project

env.user = 'root'

env.roledefs = { 'raspberry': ['192.168.1.80'], }

@roles('raspberry')
def deploy():
  rsync_project(remote_dir='/opt/home-controller/', local_dir='./')

from __future__ import with_statement
from fabric.api import *

def eggproxy(target='http://localhost:8888/'):
    env.eggproxy = target

def _pip_install(requirements='REQUIREMENTS', environment='.'):
    with settings(warn_only=True):
        if env.get('eggproxy'):
            response = local('pip install -E %s -r %s -i %s' % (environment, requirements, env.eggproxy), capture=False)
        else:
            response = local('pip install -E %s -r %s' % (environment, requirements), capture=False)
        if response.failed:
            raise Exception("Failed to install requirements", response)

def test():
    local('virtualenv .')
    _pip_install()
    local('bin/python setup.py test --xml')

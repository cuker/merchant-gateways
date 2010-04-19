from fabric.api import *
import os, time, sys


def autotest(cmd='fab test', sleep=1):  #  CONSIDER  accept app,list,comma,delimited
    """
    spin until you change a file, then run the tests

    It considers the fabfile.py directory as the project root directory, then
    monitors changes in any inner python files.

    Usage:

       fab autotest

    This is based on Jeff Winkler's nosy script.
    """

    def we_like(f):
        return f.endswith('.py') or \
               f.endswith('.html') or \
               f.endswith('.json') or \
               f.endswith('.feature') or \
               f.endswith('.xml')

    def checkSum():
        '''
        Return a long which can be used to know if any .py files have changed.
        Looks in all project's subdirectory.
        '''

        def hash_stat(file):
            from stat import ST_SIZE, ST_MTIME
            stats = os.stat(file)
            return stats[ST_SIZE] + stats[ST_MTIME]

        hash_ = 0
        base = os.path.dirname(__file__)

        for root, dirs, files in os.walk(base):
                # We are only interested int python, json, & html files
                files = [os.path.join(root, f) for f in files if we_like(f)]
                hash_ += sum(map(hash_stat, files))

        return hash_

    val = 0

    while(True):
        actual_val = checkSum()

        if val != actual_val:
            val = actual_val
            os.system(cmd)

        time.sleep(sleep)

def test():
    'run the short test batch for this project'

    _sh( 'python test.py' )




def _sh(cmd):
    local(cmd, capture=False)


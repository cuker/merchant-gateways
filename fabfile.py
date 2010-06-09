# -*- coding: utf-8 -*-
from fabric.api import *
import os, time, sys
import re

def autotest(cmd='fab soak', sleep=1):  #  CONSIDER  accept app,list,comma,delimited
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
               f.endswith('.json') or \
               f.endswith('.feature')

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


def test(extra=''):
    'run the short test batch for this project'
    cmd = 'python test.py ' + extra
    _sh( cmd.rstrip() )


def pull():
    'git pull - for short command lines like "fab pull test"'

    _sh('git pull')


def document(output='./docs/'):
    'Build docs'

    _sh("rm -rf ./docs/*")
    os.environ['PYTHONPATH'] = os.getcwd() + '/lib:' + os.environ.get('PYTHONPATH', '.')
    os.environ['PATH'] = os.environ['HOME'] + '/bin:' + os.environ['PATH']  # 2 find rite epydoc

    # ERGO  take add for WebCube out of nav bar?

    _sh( "epydoc --config=doc/epydoc.config " +
         "--graph=all --no-frames --css=doc/epydoc.css " +
         "./tests ./lib/merchant_gateways --output=" + output )


def ci(whatfo='refactor'):  #  TODO  option to invoke an editor (yilk!)
    test()
    _sh('git commit -am"%s"' % whatfo)
    _sh('git push')


def soak():
    test()
    test('--xml')
  #  document('../reports/merchant-gateways_docs/')
    report()

def _convert_test_output_to_report(test_output = 'temp/xml/test_output.xml'):
    import os
    os.system('tidy -wrap 130 -xml -i -m ' + test_output)
    output = open(test_output).read()
    return _convert_xml_to_test_report(output)

def _convert_xml_to_test_report(output, rowsPerPage = 35):  #  TODO  take out the default
    from lxml import etree  #  these are down here so if you run a fab that doesn't need them the loader does not pull them in
    from datetime import date
    doc = etree.XML(output)
    classes = {}
    parts = {}
    parts['timestamp'] = date.strftime(date.today(), '%B %d, %Y')  #  TODO match it to the xml file's mtime

#  TODO  put a rollup on the bottom

    we_be = 'Merchant Gateways'

    template = '''
        <div style="margin:1ex">
          <div style="font-family: Arial;">
            <div align="right" style="height: 123px;"><img width="316" height="38" src="http://www.zeroplayer.com/images/stuff/CukerInteractive.png"/></div>
            <div style="font-size:20pt; border-style: none none solid; border-color: black; border-width: medium medium 1.5pt; padding: 0in 0in 1pt;">
            <big>''' + we_be + '''</big><br/>
            Web Cube E-Commerce Testing Report</div>
            <p style="font-size: 12pt;"><b>%(timestamp)s</b></p>

                %(lines)s

          </div>
        </div>
        '''

    # we must paginate manually because wkhtmltopdf, the "best" PDFer out there, cannot paginate with thead tags!!!

    table_header = '''<table width="750" cellspacing="0" border="1" style="border-collapse: collapse; font-family: Arial; font-size: 10pt;">
              <thead>
                <tr valign="top" style="border: 1pt solid black; padding: 0in 5.4pt; background: black none repeat scroll 0% 0%; -moz-background-clip: border; -moz-background-origin: padding; -moz-background-inline-policy: continuous; font-size: 10pt; font-family: Arial; color: white;">
                  <th style="border: 1pt solid black;" width="120">Test</th>
                  <th style="border: 1pt solid black;">Number</th>
                  <th style="border: 1pt solid black;">Description</th>
                  <th nowrap="nowrap" style="border: 1pt solid black;">Pass / Fail</th>
                 </tr>
              </thead>
              <tbody>'''

    table_ender = '</tbody></table>'  # not "footer" because that means something else in table-land

    parts['lines'] = table_header  #  TODO  rename lines to tables

    for node in doc.xpath('//testcase'):
        classname, name = node.attrib['classname'], node.attrib.get('name', 'Morelia Feature')
        desc = node.attrib.get('desc', None)

#  TODO  Morelia's print mode should default to HTML
#  TODO  Morelia should put | bars into little tables!
#  TODO  take out the second Scenario: it's redundant

        if desc and name != 'ScenarioTest':
            desc = desc.replace('"', '&quot;'). \
                        replace('<', '&lt;').  \
                        replace('>', '&gt;')  #  TODO  use _cleanHTML
            if desc.count('\n'):
                desc = '<br/><pre>%s</pre>' % desc
            else:
                desc = '<br/><em>%s</em>' % desc
        else:
            desc = ''.join([ etree.tostring(kid) for kid in node.getchildren() if kid.tag != 'assert' ])

        name = name.replace('_', ' ')
        name = re.sub(r'^test ', '', name)
        if not desc:  desc = ''
        desc += '<ul style="color: green;">'

        for assertion in node.xpath('assert'):
            desc += '<li><small style="color: black;">'
            desc += _cleanHTML(assertion.text)
            desc += '</li></small>'

        desc += '</ul>'

        if classes.has_key(classname):
            classes[classname].append((name, desc))
        else:
            classes[classname] = [(name, desc)]

#  TODO all Rakefiles should call fab test_all (and whtat's "twill"???)
#  TODO  censor usernames & passwords from the test report
#  ERGO  promote http://wolfieartguy.deviantart.com/art/Li-l-Dragon-7188956

    keys = classes.keys()
    keys.sort()
    numRows = 0

    for major, suite in enumerate(keys):
        major += 1
        cases = classes[suite]
        cases.sort()  #  NOTE they are already sorted, but this can't hurt!
        suite = _remove_redundancies_and_add_spaces(suite)

        for minor, (case, desc) in enumerate(cases):  #  TODO  rename cases; actually put a Red in if something does not pass
            minor += 1

            if case == 'Morelia Feature':  #  TODO  now cover more than one!!!
                line = '<tr valign="top"><td colspan="5" style="font-size: 10pt;">' + desc + '</td></tr>'
            else:
                line = '''<tr valign="top">
                    <td nowrap="nowrap">%(suite)s</td>
                    <td align="center">%(number)s</td>
                    <td>%(case)s%(desc)s</td>
                    <td align="center"><img width="15" height="14" src="http://www.zeroplayer.com/images/stuff/greenCheck.png"/></td>
                  </tr>''' % dict(suite=suite, number='%i.%i' % (major, minor), case=case, desc=desc)

            numRows += 1  #  TODO  paginate story tests correctly

            if numRows > rowsPerPage:
                numRows = 0
                line = table_ender +'<p style="page-break-before: always;"/>' + table_header + line

            parts['lines'] += line

        #  TODO  redden any of them that failed
        #  TODO  are any missing?

    parts['lines'] += table_ender
    return template % parts

def _remove_redundancies_and_add_spaces(suite):
    suite = re.sub(r'Test$', '', suite)
    suite = re.sub(r'Suite$', '', suite)
    suite = re.sub(r'([A-Z])', r' \1', suite).strip()
    return suite

def _cleanHTML(whut):
    return whut.replace('"', '&quot;'). \
                replace('<', '&lt;').  \
                replace('>', '&gt;')


def report():
    'format a recent test run (without running it again!)'

    html = _convert_test_output_to_report('TEST-unittest.TestSuite.xml')

    name = 'merchant-gateways'
    from os import path
    import os

    if not path.exists('../reports'): os.mkdir('../reports')
    html_filename = '../reports/%s_report.html' % name
    pdf_filename = '../reports/%s_report.pdf' % name
    open(html_filename, 'w').write(html.encode('utf-8'))
    _sh('xvfb-run -a -s "-screen 0 640x480x16" wkhtmltopdf %s %s' % (html_filename, pdf_filename))


def _sh(cmd):
    local(cmd, capture=False)



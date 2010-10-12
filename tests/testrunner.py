import unittest
import os
import sys

def runtests():
    print 'start...'
    suite = unittest.defaultTestLoader.loadTestsFromNames(['tests.unit.avs_result_test',
                                                           'tests.unit.cvv_result_test',
                                                           'tests.unit.credit_card_tests',
                                                           'tests.unit.gateways.authorize_net_tests',
                                                           'tests.unit.gateways.bogus_tests',
                                                           'tests.unit.gateways.braintree_blue_tests',
                                                           'tests.unit.gateways.braintree_orange_tests',
                                                           'tests.unit.gateways.cybersource_tests',
                                                           'tests.unit.gateways.payflow_tests',
                                                           'tests.unit.gateways.paymentech_orbital_tests',])
    if os.environ.get('XML_OUTPUT', False):
        from xmlrunner import XMLTestRunner
        runner = XMLTestRunner()
        print 'xml ftw'
    else:
        runner = unittest.TextTestRunner(verbosity=1, descriptions=False)
    print 'running'
    result = runner.run(suite).wasSuccessful()
    print result
    exit_code = result and 0 or 1
    print exit_code
    sys.exit(exit_code)

if __name__ == '__main__':
    runtests()

import unittest
import os
import sys

def runtests():
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
    else:
        runner = unittest.TextTestRunner(verbosity=1, descriptions=False)
    sys.exit(runner.run(suite).wasSuccessful() and 0 or 1)

if __name__ == '__main__':
    runtests()

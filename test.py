
from os import path
here = path.dirname(path.abspath(__file__))
import sys;
sys.path.append(here + '/lib')
import unittest

from tests.unit.avs_result_test import *
from tests.unit.cvv_result_test import *
# from tests.unit.credit_card_formatting_tests import *
# from tests.unit.credit_card_methods_tests import *
from tests.unit.credit_card_tests import *
from tests.unit.gateways.authorize_net_tests import *  #  TODO  import all in tests?
from tests.unit.gateways.bogus_tests import *
from tests.unit.gateways.braintree_gateway_tests import *
from tests.unit.gateways.braintree_orange_tests import *
from tests.unit.gateways.cybersource_tests import *
from tests.unit.gateways.payflow_tests import *
from tests.unit.gateways.paymentech_orbital_tests import *

#  TODO  import with from future in fab system and test utils

if sys.argv.count('--xml'):
    sys.argv.remove('--xml')
    from tests.xmlrunner import XMLTestRunner
    runner = XMLTestRunner()
else:
    runner = unittest.TextTestRunner(verbosity=1, descriptions=False)

unittest.main(testRunner=runner)


from os import path
here = path.dirname(path.abspath(__file__))
import sys;
sys.path.append(here + '/lib')
sys.path.append(here + '/..')
import unittest

from tests.unit.avs_result_test import *
from tests.unit.cvv_result_test import *
#from tests.unit.credit_card_formatting_tests import *
#from tests.unit.credit_card_methods_tests import *
from tests.unit.credit_card_tests import *
from tests.unit.gateways.authorize_net_tests import *  #  TODO  import all in tests?
from tests.unit.gateways.cybersource_tests import *
from tests.unit.gateways.payflow_tests import *

#  TODO  rename our home folder
#  TODO  import with from future in fab system and test utils

runner = unittest.TextTestRunner(verbosity=1, descriptions=False)  #  TODO  help this feeb test runner not hug a nut!
unittest.main(testRunner=runner)

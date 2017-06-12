"""
Base class for all IXN package tests.

@author yoram@ignissoft.com
"""

from os import path

from trafficgenerator.test.test_tgn import TgnTest

from ixnetwork.api.ixn_tcl import IxnTclWrapper
from ixnetwork.api.ixn_python import IxnPythonWrapper
from ixnetwork.api.ixn_rest import IxnRestWrapper
from ixnetwork.ixn_app import IxnApp


class IxnTestBase(TgnTest):

    TgnTest.config_file = path.join(path.dirname(__file__), 'IxNetwork.ini')

    def setUp(self):
        super(IxnTestBase, self).setUp()
        if self.config.get('IXN', 'api').lower() == 'tcl':
            api_wrapper = IxnTclWrapper(self.logger, self.config.get('IXN', 'install_dir'))
        elif self.config.get('IXN', 'api').lower() == 'python':
            api_wrapper = IxnPythonWrapper(self.logger, self.config.get('IXN', 'install_dir'))
        else:
            api_wrapper = IxnRestWrapper(self.logger)
        self.ixn = IxnApp(self.logger, api_wrapper=api_wrapper)
        self.ixn.connect(self.config.get('IXN', 'api_server'), self.config.get('IXN', 'api_port'))

    def tearDown(self):
        super(IxnTestBase, self).tearDown()

    def testHelloWorld(self):
        pass

    #
    # Auxiliary functions, no testing inside.
    #

    def _load_config(self, config_file):
        self.ixn.new_config()
        self.ixn.load_config(config_file)
        self.ixn.commit()

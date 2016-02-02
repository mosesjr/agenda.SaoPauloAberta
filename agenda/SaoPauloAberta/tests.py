import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import agenda.SaoPauloAberta

OPTION_FLAGS = doctest.NORMALIZE_WHITESPACE | \
               doctest.ELLIPSIS

ptc.setupPloneSite(products=['agenda.SaoPauloAberta'])


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            zcml.load_config('configure.zcml',
              agenda.SaoPauloAberta)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='agenda.SaoPauloAberta',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='agenda.SaoPauloAberta.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'INTEGRATION.txt',
            package='agenda.SaoPauloAberta',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),

        # -*- extra stuff goes here -*-

        # Integration tests for AgendaDoPrefeito
        ztc.ZopeDocFileSuite(
            'AgendaDoPrefeito.txt',
            package='agenda.SaoPauloAberta',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for TipoAgendaDoPrefeito
        ztc.ZopeDocFileSuite(
            'TipoAgendaDoPrefeito.txt',
            package='agenda.SaoPauloAberta',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

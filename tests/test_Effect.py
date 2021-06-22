import inkex

import unittest
#import mock

from inkscape_helper.Effect import Effect
eff = Effect()

class TestEffect(unittest.TestCase):

    def setUp(self):
        self.eff = inkex.Effect()
        self.eff.run(['empty.svg'])

    def test_known_units(self):
        self.assertIn('cm', eff.knownUnits)

    def test_unittouu(self):
        self.assertEqual(self.eff.unittouu('0 cm'), 0)

    def test_options(self):
        options = []
        options.append(['optname', int])
        options.append(['othername', str, 'default', 'help text'])

        eff = Effect(options)
        self.assertIsInstance(eff, Effect)

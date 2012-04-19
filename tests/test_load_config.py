import os, sys
from bf3stats import Bf3StatsPlugin
from tests import Bf3TestCase

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from b3.config import CfgConfigParser

class Test_default_config(unittest.TestCase):
    def setUp(self):
        self.conf = CfgConfigParser()
        self.conf.load(os.path.join(os.path.dirname(__file__), '../extplugins/conf/plugin_bf3stats.ini'))

    def test_bf3stats_exists(self):
        self.assertEqual(0, self.conf.getint('commands', 'bf3stats'))

    def test_bf3stats_com(self):
        self.assertTrue(self.conf.has_section("bf3stats.com"))
        self.assertTrue(self.conf.has_option("bf3stats.com", "ident"))
        self.assertTrue(self.conf.has_option("bf3stats.com", "secret_key"))

    def test_make_sure_default_config_has_no_secret(self):
        self.assertEqual('', self.conf.get("bf3stats.com", "ident"))
        self.assertEqual('', self.conf.get("bf3stats.com", "secret_key"))

    def test_preferences(self):
        self.assertEqual(40, self.conf.getint("preferences", "minimum_level_to_update_stats"))


class Test_preferences(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = Bf3StatsPlugin(self.console, self.conf)

    def test_default_value(self):
        self.conf.loadFromString("""[preferences]""")
        self.p._load_config_preferences()
        self.assertEqual(128, self.p.minimum_level_to_update_stats)

    def test_nominal(self):
        self.conf.loadFromString("""[preferences]
minimum_level_to_update_stats: 20""")
        self.p._load_config_preferences()
        self.assertEqual(20, self.p.minimum_level_to_update_stats)

    def test_too_small(self):
        self.conf.loadFromString("""[preferences]
minimum_level_to_update_stats: -1""")
        self.p._load_config_preferences()
        self.assertEqual(128, self.p.minimum_level_to_update_stats)

    def test_too_big(self):
        self.conf.loadFromString("""[preferences]
minimum_level_to_update_stats: 130""")
        self.p._load_config_preferences()
        self.assertEqual(128, self.p.minimum_level_to_update_stats)

class Test_bf3stats_com(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.p = Bf3StatsPlugin(self.console, self.conf)

    def test_default_value(self):
        self.conf.loadFromString("""[bf3stats.com]""")
        self.p._load_config_bf3stats()
        self.assertIsNone(self.p.ident)
        self.assertIsNone(self.p.secret_key)

    def test_nominal(self):
        self.conf.loadFromString("""[bf3stats.com]
ident: foo
secret_key: bar""")
        self.p._load_config_bf3stats()
        self.assertEqual("foo", self.p.ident)
        self.assertEqual("bar", self.p.secret_key)

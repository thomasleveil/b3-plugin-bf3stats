import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import logging
from mockito import when
from mock import patch
from b3.update import B3version
from b3 import TEAM_UNKNOWN
from b3.config import XmlConfigParser
from b3.parsers.bf3 import Bf3Parser
from b3.plugins.admin import AdminPlugin
from b3 import __version__ as b3_version


class logging_disabled(object):
    """
    context manager that temporarily disable logging.

    USAGE:
        with logging_disabled():
            # do stuff
    """
    DISABLED = False

    def __init__(self):
        self.nested = logging_disabled.DISABLED

    def __enter__(self):
        if not self.nested:
            logging.getLogger('output').propagate = False
            logging_disabled.DISABLED = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.nested:
            logging.getLogger('output').propagate = True
            logging_disabled.DISABLED = False


class Bf3TestCase(unittest.TestCase):
    """
    Test case that is suitable for testing BF3 parser specific features
    """

    @classmethod
    def setUpClass(cls):
        with logging_disabled():
            from b3.parsers.frostbite2.abstractParser import AbstractParser
            from b3.fake import FakeConsole
            AbstractParser.__bases__ = (FakeConsole,)
            # Now parser inheritance hierarchy is :
            # Bf3Parser -> AbstractParser -> FakeConsole -> Parser

            # add method changes_team(newTeam, newSquad=None) to FakeClient
            def changes_team(self, newTeam, newSquad=None):
                self.console.OnPlayerTeamchange(data=[self.cid, newTeam, newSquad if newSquad else self.squad], action=None)

            from b3.fake import FakeClient
            FakeClient.changes_team = changes_team

    def setUp(self):
        # create a BF3 parser
        self.parser_conf = XmlConfigParser()
        self.parser_conf.loadFromString("""
                    <configuration>
                    </configuration>
                """)
        self.console = Bf3Parser(self.parser_conf)
        self.console.startup()

        # load the admin plugin
        if B3version(b3_version) >= B3version("1.10dev"):
            admin_plugin_conf_file = '@b3/conf/plugin_admin.ini'
        else:
            admin_plugin_conf_file = '@b3/conf/plugin_admin.xml'
        with logging_disabled():
            self.adminPlugin = AdminPlugin(self.console, admin_plugin_conf_file)
            self.adminPlugin.onStartup()

        # make sure the admin plugin obtained by other plugins is our admin plugin
        when(self.console).getPlugin('admin').thenReturn(self.adminPlugin)

        # prepare a few players
        from b3.fake import FakeClient
        self.joe = FakeClient(self.console, name="Joe", exactName="Joe", guid="zaerezarezar", groupBits=1, team=TEAM_UNKNOWN, teamId=0, squad=0)
        self.simon = FakeClient(self.console, name="Simon", exactName="Simon", guid="qsdfdsqfdsqf", groupBits=0, team=TEAM_UNKNOWN, teamId=0, squad=0)
        self.reg = FakeClient(self.console, name="Reg", exactName="Reg", guid="qsdfdsqfdsqf33", groupBits=4, team=TEAM_UNKNOWN, teamId=0, squad=0)
        self.moderator = FakeClient(self.console, name="Moderator", exactName="Moderator", guid="sdf455ezr", groupBits=8, team=TEAM_UNKNOWN, teamId=0, squad=0)
        self.admin = FakeClient(self.console, name="Level-40-Admin", exactName="Level-40-Admin", guid="875sasda", groupBits=16, team=TEAM_UNKNOWN, teamId=0, squad=0)
        self.superadmin = FakeClient(self.console, name="God", exactName="God", guid="f4qfer654r", groupBits=128, team=TEAM_UNKNOWN, teamId=0, squad=0)

        # a few mocks
        self.say_patcher = patch.object(self.console, 'say')
        self.say_mock = self.say_patcher.start()

        self.write_patcher = patch.object(self.console, 'write')
        self.write_mock = self.write_patcher.start()


    def tearDown(self):
        self.console.working = False
        self.write_patcher.stop()
        self.say_patcher.stop()

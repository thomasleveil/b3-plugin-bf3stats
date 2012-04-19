#
# Bf3stats for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2012 courgette@bigbrotherbot.net
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import ConfigParser
import time
from b3.plugin import  Plugin
from b3.functions import minutesStr
from bf3stats.api import API
from bf3stats.playerstats import PlayerStats, Bf3statsError, NoStat

from bf3stats import __version__ as plugin_version
from bf3stats.playerupdate import Bf3stats_player_update_service

__version__ = plugin_version # hack to get the plugin version correctly reported to B3 master servers


class Bf3StatsPlugin(Plugin):
    def __init__(self, console, config=None):
        self.ident = None
        self.secret_key = None
        self.bf3stats_api = None
        self.age_triggering_player_update = 60 * 60 * 24 * 7
        Plugin.__init__(self, console, config)

    ################################################################################################################
    #
    #    Plugin interface implementation
    #
    ################################################################################################################

    def onLoadConfig(self):
        """\
        This is called after loadConfig(). Any plugin private variables loaded
        from the config need to be reset here.
        """
        self._load_config_bf3stats()
        self._load_config_preferences()
        self.bf3stats_api = API(ident=self.ident, secret=self.secret_key)


    def onStartup(self):
        """\
        Initialize plugin settings
        """
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
        self._registerCommands()
        self.update_service = Bf3stats_player_update_service(self.bf3stats_api)


    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        pass


    ################################################################################################################
    #
    #   Commands implementations
    #
    ################################################################################################################

    def cmd_bf3stats(self, data, client, cmd=None):
        """\
        [player] - query bf3stats.com for stats of player
        """
        targetted_player = None
        if data:
            targetted_player = self._adminPlugin.findClientPrompt(data, client)
            if not targetted_player:
                # a player matching the name was not found, a list of closest matches will be displayed
                # we can exit here and the user will retry with a more specific player
                return
        if not targetted_player:
            targetted_player = client

        if self.ident and self.secret_key and client.maxLevel >= self.minimum_level_to_update_stats:
            self.do_cmd_bf3stats_with_update(client, targetted_player, cmd)
        else:
            self.do_cmd_bf3stats_without_update(client, targetted_player, cmd)


    ################################################################################################################
    #
    #    Other methods
    #
    ################################################################################################################

    def _registerCommands(self):
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp
                func = getattr(self, "cmd_" + cmd, None)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
                else:
                    self.warning("config defines unknown command '%s'" % cmd)

    def get_updated_stats(self, player):
        assert hasattr(player, "name")
        CACHE_TTL_SECONDS = 60 * 5
        bf3stats_var = player.var(self, "bf3stats", None)
        if not bf3stats_var or bf3stats_var.value is None or time.time() - bf3stats_var.value.date_update > CACHE_TTL_SECONDS:
            bf3stats = PlayerStats(self.bf3stats_api, player.name)
            self.debug("received stats from bf3stats.com : %r" % bf3stats.data)
            bf3stats_var = player.setvar(self, "bf3stats", bf3stats)
        return bf3stats_var.value

    def _load_config_bf3stats(self):
        try:
            ident = self.config.get("bf3stats.com", "ident")
        except ConfigParser.NoOptionError, err:
            ident = None
        try:
            secret_key = self.config.get("bf3stats.com", "secret_key")
        except ConfigParser.NoOptionError, err:
            secret_key = None
        if ident and secret_key:
            self.info(
                "bf3stats.com ident/secret_key pair found in config. Player stats updates will be requested if too old")
            self.ident = ident
            self.secret_key = secret_key
        elif ident is None and secret_key is None:
            self.info("No bf3stats.com ident/secret_key pair found in config. Player stats updates won't be requested")
        elif ident or secret_key:
            self.warning(
                "No bf3stats.com ident/secret_key pair found in config. Player stats updates won't be requested")

    def _load_config_preferences(self):
        self.minimum_level_to_update_stats = 128 # by default only superadmin can request updates
        try:
            data = self.config.getint("preferences", "minimum_level_to_update_stats")
            if not 0 <= data <= 128:
                raise ValueError("preferences\minimum_level_to_update_stats must be between 0 and 128")
        except ConfigParser.NoOptionError, err:
            self.debug(err)
            self.warning(
                "setting preferences\minimum_level_to_update_stats not found in config. Falling back on default value")
        except ValueError, err:
            self.debug(err)
            self.warning(
                "Invalid value for setting preferences\minimum_level_to_update_stats. Falling back on default value. %s" % err)
        except Exception, err:
            self.error(err)
        else:
            self.minimum_level_to_update_stats = data
        finally:
            self.info(
                "setting preferences\minimum_level_to_update_stats is : " + str(self.minimum_level_to_update_stats))


    def callback_player_update(self, client, targetted_player, cmd, data):
        if data.status == "notask":
            # no credit left to request update
            client.message("Bf3stats.com hourly limit reached. Can't update stats until next hour")
        elif hasattr(data, "Task") and data.Task.state == "finished":
            self.do_cmd_bf3stats_without_update(client, targetted_player, cmd)
        else:
            self.debug(data)
            err = data.status
            if data.status == 'error':
                err = data.error
            client.message("Bf3stats.com failed to update stats for '%s' (%s)" % (targetted_player.name, err))


    def __send_bf3stats_response(self, client, targetted_player, cmd, stats):
        def short_minuteStr(text):
            return minutesStr(text).replace(" seconds", "s").replace(" second", "s").replace(" minutes", "min").replace(" minute", "min").replace(" hours", "hr").replace(" hour", "hr")
        if cmd.loud or cmd.big:
            self.console.say("bf3stats.com for %s : (upd %s ago)" % (targetted_player.name,  short_minuteStr("%ss" % stats.data_age)))
            self.console.say(str(stats))
            if cmd.big:
                self.console.write(('admin.yell', "bf3stats.com for %s : %s" % (targetted_player.name, stats), 10, 'all'))
        else:
            self.console.say("bf3stats.com for %s : (upd %s ago)" % (targetted_player.name,  short_minuteStr("%ss" % stats.data_age)))
            self.console.say(str(stats))
            self.console.write(('admin.yell', str(stats), 10, 'player', client.cid))

    def do_cmd_bf3stats_without_update(self, client, targetted_player, cmd):
        try:
            stats = self.get_updated_stats(targetted_player)
        except NoStat:
            client.message("bf3stats.com has no stats for %s" % targetted_player.name)
        except Bf3statsError, err:
            client.message("Error while querying bf3stats.com. %s" % err)
        else:
            self.__send_bf3stats_response(client, targetted_player, cmd, stats)

    def do_cmd_bf3stats_with_update(self, client, targetted_player, cmd):
        try:
            stats = self.get_updated_stats(targetted_player)
        except NoStat:
            client.message("bf3stats.com has no stats for %s, requesting update..." % targetted_player.name)
            self.update_service.request_update(player_name=targetted_player.name, client=client,
                callback=self.callback_player_update, callback_args=(client, targetted_player, cmd))
        except Bf3statsError, err:
            client.message("Error while querying bf3stats.com. %s" % err)
        else:
            self.__send_bf3stats_response(client, targetted_player, cmd, stats)
            if stats.data_age > self.age_triggering_player_update:
                client.message("stats are more than %s old, requesting update..." % minutesStr(
                    "%ss" % self.age_triggering_player_update))
                self.update_service.request_update(player_name=targetted_player.name, client=client,
                    callback=self.callback_player_update, callback_args=(client, targetted_player, cmd))

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
import time
from b3.plugin import  Plugin
from b3.functions import minutesStr
from bf3stats.playerstats import PlayerStats, Bf3statsError, NoStat


class Bf3StatsPlugin(Plugin):

    def __init__(self, console, config=None):
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
        pass


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
        try:
            stats = self.get_updated_stats(targetted_player)
        except NoStat:
            client.message("bf3stats.com has no stats for %s" % targetted_player.cid)
        except Bf3statsError, err:
            client.message("Error while querying bf3stats.com. %s" % err)
        else:
            text = "%s | updated %s ago" % (stats, minutesStr("%ss" % stats.data_age))
            if cmd.loud:
                self.console.say("bf3stats.com for %s : %s" % (targetted_player.cid, text))
            elif cmd.big:
                self.console.write(('admin.yell', "bf3stats.com for %s : %s" % (targetted_player.cid, text), 10, 'all'))
            else:
                self.console.write(('admin.say', text, 'player', client.cid))
                self.console.write(('admin.yell', text, 10, 'player', client.cid))


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
        CACHE_TTL_SECONDS = 60 * 5
        bf3stats_var = player.var(self, "bf3stats", None)
        if not bf3stats_var or bf3stats_var.value is None or time.time() - bf3stats_var.value.date_update > CACHE_TTL_SECONDS:
            bf3stats = PlayerStats(player.name)
            self.debug(repr(bf3stats.data))
            bf3stats_var = player.setvar(self, "bf3stats", bf3stats)
        return bf3stats_var.value


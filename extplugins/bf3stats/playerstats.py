import time
from bf3stats.api import API

class Bf3statsError(Exception):
    def __init__(self, name, data):
        Exception.__init__(self, name)
        self.data = data

class NoStat(Bf3statsError):
    def __init__(self, playername, data):
        Bf3statsError.__init__(self, "Player '%s' found but has no stats" % playername, data)

class NotFound(Bf3statsError):
    def __init__(self, playername, data):
        Bf3statsError.__init__(self, "Player '%s' not found" % playername, data)

class InvalidName(Bf3statsError):
    def __init__(self, playername, data):
        Bf3statsError.__init__(self, "Invalid name '%s'" % playername, data)

class Error(Bf3statsError):
    def __init__(self, playername, data):
        Bf3statsError.__init__(self, "Error while querying '%s' : %s" % (playername, data.error), data)



class PlayerStats(object):

    def __init__(self, bf3stats_api, playername):
        bf3stats_service = bf3stats_api
        data = bf3stats_service.player(playername, 'clear,global,scores,rank')
        if not data:
            raise Bf3statsError("no data received from bf3stats.com", None)
        else:
            if not hasattr(data, 'status'):
                raise Bf3statsError("bad response", data)
            elif data.status == 'data':
                self.data = data
            elif data.status == 'notfound':
                raise NotFound(playername, data)
            elif data.status == 'invalid_name':
                raise InvalidName(playername, data)
            elif data.status == 'pifound':
                raise NoStat(playername, data)
            elif data.status == 'error':
                raise Error(playername, data)
            else:
                raise Bf3statsError("unknown status '%s'" % data.status)

    @property
    def date_update(self):
        return self.data.Stats.date_update

    @property
    def data_age(self):
        return time.time() - self.date_update

    @property
    def skill(self):
        """ skill (ELO) """
        return self.data.Stats.Global.elo

    @property
    def accuracy(self):
        """ accuracy % """
        return round(1.0 * self.data.Stats.Global.hits / self.data.Stats.Global.shots * 100, 1)
    
    @property
    def winlossratio(self):
        """ Wins / Losses ratio """
        return round(1.0 * self.data.Stats.Global.wins / self.data.Stats.Global.losses, 2)

    @property
    def killdeathratio(self):
        """ Kills / Deaths ratio """
        return round(1.0 * self.data.Stats.Global.kills / self.data.Stats.Global.deaths, 2)

    @property
    def nemesiskillspct(self):
        """ % of nemesis kills """
        return round(1.0 * self.data.Stats.Global.nemesiskills / self.data.Stats.Global.kills * 100, 2)

    @property
    def scoreperminute(self):
        """ global score / minutes of game played """
        return int(round(1.0 * self.data.Stats.Scores.score / self.data.Stats.Global.time * 60))

    def __str__(self):
        return "skill:%s | Sc/min:%s | W/L:%s | K/D:%s | Acc:%s%% | Nemesis:%s%%" % (self.skill, self.scoreperminute, self.winlossratio, self.killdeathratio, self.accuracy, self.nemesiskillspct)

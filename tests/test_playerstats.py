import sys
from bf3stats.api import API

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from mock import patch, Mock
from bf3stats.playerstats import PlayerStats, NotFound, Bf3statsError
from StringIO import StringIO

urlopen_nominal_mock = Mock(return_value=StringIO("""
        {
            "plat":"pc","name":"someone","language":"fr","country":"fr","country_name":"France","date_insert":1320347509,"date_update":1320347509,
            "stats":{
                "date_insert":1320347510,"date_update":1334345184,"date_check":1334345550,"checkstate":"nochange",
                "rank":{
                    "nr":46,"name":"COLONEL SERVICE STAR 1","score":1830000
                },
                "scores":{
                    "score":2013970,"award":798200,"assault":234624,"bonus":31800,"engineer":272744,"general":889052,
                    "objective":103750,"recon":129671,"squad":80810,"support":200102,"team":55955,"unlock":54400,"vehicleaa":18688,
                    "vehicleah":7656,"vehicleall":324226,"vehicleifv":32200,"vehiclejet":1180,"vehiclembt":263552,"vehiclesh":950
                },
                "global":{
                    "kills":4533,"deaths":4217,"wins":209,"losses":278,"shots":258327,"hits":50699,"headshots":944,"longesths":690.37,
                    "time":531683,"vehicletime":147633,"vehiclekills":780,"revives":204,"killassists":468.88,"resupplies":730,
                    "heals":7368.96,"repairs":1267.15,"rounds":624,"elo":338.2,"elo_games":487,"killstreakbonus":14,
                    "vehicledestroyassist":102.1,"vehicledestroyed":501,"dogtags":66,"avengerkills":295,"saviorkills":114,"damagaassists":28,
                    "suppression":184,"nemesisstreak":7,"nemesiskills":59,"mcomdest":7,"mcomdefkills":7,"flagcaps":583,"flagdef":415,
                    "longesthandhs":690.37
                }
            },"status":"data"
        }"""))

urlopen_not_found_mock = Mock(return_value=StringIO("""{"status":"notfound"}"""))


class Test_PlayerStats(unittest.TestCase):
    def test_str(self):
        with patch("urllib.urlopen", new=urlopen_nominal_mock):
            ps = PlayerStats(API(), 'someone')
            self.assertEqual('skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | H/K:0.21', str(ps))


    def test_non_existing_player(self):
        with patch("urllib.urlopen", new=urlopen_not_found_mock):
            try:
                PlayerStats(API(), 'someone')
            except NotFound:
                pass
            except Bf3statsError, err:
                self.fail("expected NofFound error but got : %r" % err)
            else:
                self.fail("execpted NotFound error")
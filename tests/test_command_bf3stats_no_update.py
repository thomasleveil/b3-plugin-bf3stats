from mock import patch, Mock, call
import time
from b3.config import CfgConfigParser
from bf3stats import Bf3StatsPlugin
from StringIO import StringIO
from tests import Bf3TestCase

def provide_stats_feed(*args, **kwargs):
    return StringIO("""
        {
            "plat":"pc","name":"Someone","language":"fr","country":"fr","country_name":"France","date_insert":1320347509,"date_update":1334345184,
            "stats":{
                "date_insert":1320347510,"date_update":%(date_updated)s,"date_check":1334345550,"checkstate":"nochange",
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
        }""" % {'date_updated': time.time() - (5 * 60 * 60)})

urlopen_nominal_mock = Mock(wraps=provide_stats_feed)


@patch("urllib.urlopen", new=urlopen_nominal_mock)
class Test_status_data(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.conf.loadFromString("""
[commands]
bf3stats: 0
""")
        self.p = Bf3StatsPlugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

    def test_nominal_no_argument(self):
        self.joe.connects('joe')
        self.joe.says("!bf3stats")
        self.write_mock.assert_has_calls([
            call(('admin.say', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 'player', 'joe')),
            call(('admin.yell', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 10, 'player', 'joe')),
            ])

    def test_nominal_with_argument(self):
        self.joe.connects('joe')
        self.admin.connects('admin')
        self.admin.says("!bf3stats joe")
        self.assertEqual([], self.admin.message_history)
        self.write_mock.assert_has_calls([call(('admin.say', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 'player', 'admin')),
                                          call(('admin.yell', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 10, 'player', 'admin'))])

    def test_with_argument_inexistant_player(self):
        self.admin.connects('admin')
        self.admin.says("!bf3stats joe")
        self.assertEqual(['No players found matching joe'], self.admin.message_history)

    def test_loud_no_privilege(self):
        self.joe.connects('joe')
        self.joe.says("@bf3stats")
        self.write_mock.assert_has_calls([
            call(('admin.say', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 'player', 'joe')),
            call(('admin.yell', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 10, 'player', 'joe')),
            ])

    def test_big_no_privilege(self):
        self.joe.connects('joe')
        self.joe.says("&bf3stats")
        self.write_mock.assert_has_calls([call(('admin.say', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 'player', 'joe')),
                                          call(('admin.yell', 'skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 10, 'player', 'joe'))])

    def test_loud(self):
        self.admin.connects('admin')
        self.admin.says("@bf3stats")
        self.say_mock.assert_has_calls([call('bf3stats.com for admin : skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago')])

    def test_big(self):
        self.admin.connects('admin')
        self.admin.says("&bf3stats")
        self.write_mock.assert_has_calls([call(('admin.yell', 'bf3stats.com for admin : skill:338.2 | Sc/min:227 | W/L:0.75 | K/D:1.07 | Acc:19.6% | Nemesis:1.3% | updated 5 hours ago', 10, 'all'))])



urlopen_not_found_mock = Mock(return_value = StringIO("""{"status":"notfound"}"""))
urlopen_invalid_name_mock = Mock(return_value = StringIO('{"status": "error", "reasons": ["too long"], "error": "invalid_name"}'))
urlopen_pifound_mock = Mock(return_value = StringIO("""{"status":  "pifound", "country_img": "flags/fr.png", "stats": null, "name": "diokless", "language": "fr", "country": "fr", "date_update": 1321788634, "plat": "pc", "country_name": "France", "date_insert": 1321788635}"""))

class Test_other_statuses(Bf3TestCase):
    def setUp(self):
        Bf3TestCase.setUp(self)
        self.conf = CfgConfigParser()
        self.conf.loadFromString("""
[commands]
bf3stats: 0
""")
        self.p = Bf3StatsPlugin(self.console, self.conf)
        self.p.onLoadConfig()
        self.p.onStartup()

    @patch("urllib.urlopen", new=urlopen_not_found_mock)
    def test_not_found(self):
        self.joe.connects('Joe')
        self.joe.says("!bf3stats")
        self.assertEqual(["Error while querying bf3stats.com. Player 'Joe' not found"], self.joe.message_history)

    @patch("urllib.urlopen", new=urlopen_invalid_name_mock)
    def test_invalid_name(self):
        self.joe.connects('Joe')
        self.joe.says("!bf3stats")
        self.assertEqual(["Error while querying bf3stats.com. Error while querying 'Joe' : invalid_name"], self.joe.message_history)

    @patch("urllib.urlopen", new=urlopen_pifound_mock)
    def test_pifound(self):
        self.joe.connects('Joe')
        self.joe.says("!bf3stats")
        self.assertEqual(['bf3stats.com has no stats for Joe'], self.joe.message_history)
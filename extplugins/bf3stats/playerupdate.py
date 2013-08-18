from threading import Thread, Lock
import time


class Bf3stats_player_update_service(object):
    """Class implementing a service which requests player stats updates to the bf3stats.com service. It can receive
    multiple update requests for the same player from different parties and will detect that situation and avoid
    spamming the bf3stats.com service with the same requests while insuring that all parties will get the result once
    obtained from bf3stats.com"""

    def __init__(self, bf3stats_api):
        self.__bf3stats_api = bf3stats_api
        self.__lock = Lock() # to protect access to self.__running_tasks
        self.__running_tasks = {} # key: player name we requests stats update for, values: list of callback methods + args

    def on_task_done(self, player_name, data):
        if player_name in self.__running_tasks:
            while True:
                with self.__lock:
                    try:
                        idclient, (callback, args) = self.__running_tasks[player_name].popitem()
                    except KeyError:
                        del self.__running_tasks[player_name]
                        break
                try:
                    callback(*args, data=data)
                finally:
                    # Avoid a refcycle if the thread is running a function with
                    # an argument that has a member that points to the thread.
                    del callback, args

    def request_update(self, player_name, client, callback=None, callback_args=()):
        """
        player_name: the name of the player we want fresh stats for
        client: the Client object for the person requesting the update
        callback: function to call once stats received
        callback_args: args for the callback function

        Additionally the callback function will be called with a named parameter 'data' which is the data received from
        bf3stats.com
        """
        with self.__lock:
            if not player_name in self.__running_tasks:
                self.__running_tasks[player_name] = {}
                Bf3stats_player_update(self.__bf3stats_api, player_name, callback=self.on_task_done,
                                       callback_args=(player_name,)).start()
            self.__running_tasks[player_name][id(client)] = (callback, callback_args)


class Bf3stats_player_update(Thread):
    """Thread that send a player update requests to the bf3stasts.com server and poll until it get the result of this
    async task. Once the result obtained, send call the callback function with the callback_args as parameter and the
    named parameter 'data' which contains the bf3stats.com response"""

    def __init__(self, bf3stats_api, player_name, name=None, verbose=None, callback=None, callback_args=()):
        Thread.__init__(self, name=name, verbose=verbose)
        self.daemon = True
        self.__bf3stats_api = bf3stats_api
        self.__player_name = player_name
        self.__callback = callback
        self.__callback_args = callback_args

    def run(self):
        """call api.playerupdate(player_name) until update is done or failed"""
        data = self.__bf3stats_api.playerupdate(self.__player_name)
        if data.status == "added":
            while True:
                time.sleep(10.2)
                data = self.__bf3stats_api.playerupdate(self.__player_name)
                if data.status != "exists" or data.Task.state == "finished":
                    break
        try:
            if self.__callback:
                self.__callback(*self.__callback_args, data=data)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self.__callback, self.__callback_args
from threading import Thread
import time

def _to_str(name):
    """Add _ if given string is a digit."""
    if name.isdigit():
        name = '_%s' % name

    return name


class Bf3stats_player_update(Thread):

    def __init__(self, bf3stats_api, player_name, name=None, verbose=None, callback=None, callback_args=(), callback_kwargs=None):
        Thread.__init__(self, name=name, verbose=verbose)
        self.daemon = True
        self.__bf3stats_api = bf3stats_api
        self.__player_name = player_name
        self.__callback = callback
        self.__callback_args = callback_args
        self.__callback_kwargs = callback_kwargs

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
                self.__callback(*self.__callback_args, data=data, **self.__callback_kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self.__callback, self.__callback_args, self.__callback_kwargs


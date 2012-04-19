BF3stats plugin for Big Brother Bot (www.bigbrotherbot.net)
===========================================================


Description
-----------

This plugin provides a command which can query the `bf3stats.com <http://bf3stats.com>`_ website for stats about players.

Bf3stats.com service does only refresh players stats on request, either by searching a player on the `bf3stats.com <http://bf3stats.com>`_ website or using a `registered app key <http://bf3stats.com/site/api/apps>`_.

If you go on `http://bf3stats.com/site/api/apps <http://bf3stats.com/site/api/apps>`_ and register your plugin in the *Register App* form, then you will be given a *ident*/*secret_key* pair that you can set in this plugin config file. This will allow the plugin to request updates for you.


.. image:: http://i.imgur.com/XcvyI.png
   :alt: In-game screenshot
   :target: http://imgur.com/XcvyI
   :align: center


Requirements
------------

- This plugin only works for BF3 servers
- B3 v1.8.2dev2 or later


Installation
------------

- copy the bf3stats folder into b3/extplugins
- copy the plugin_bf3stats.ini file into your b3 config folder
- add to the plugins section of your main b3 config file::

    <plugin name="bf3stats" config="@conf/plugin_bf3stats.ini" />


Commands
--------

!bf3stats or /bf3stats
  display your own stats

!bf3stats <player> or /bf3stats <player>
  display stats for player to the user using the command



Support
-------

Support is only provided on www.bigbrotherbot.net forums on the following topic : http://bit.ly/HUCyw3



Credit
------

This plugin has been make possible thanks to :

- `Ozon's work <https://github.com/ozon/python-bf3stats>`_
- `P-STATS.com <http://p-stats.com/>`_

.. image:: http://files.p-stats.com/img/pstats/pstats_logo.png
     :alt: Player Stats Network
     :target: http://p-stats.com/
     :scale: 50%

Contrib
-------

- *features* can be discussed on the `B3 forums <http://bit.ly/HUCyw3>`_
- documented and reproducible *bugs* can be reported on the `issue tracker <https://github.com/courgette/b3-plugin-bf3stats/issues>`_
- *patches* are welcome. Send me a `pull request <http://help.github.com/send-pull-requests/>`_. It is best if your patch provides tests.

.. image:: https://secure.travis-ci.org/courgette/b3-plugin-bf3stats.png?branch=master
   :alt: Build Status
   :target: http://travis-ci.org/courgette/b3-plugin-bf3stats


Changelog
---------

1.0
  first release which can query players' stats from bf3stats.com

1.1
  can now request stats update on bf3stats.com given that you registered your app

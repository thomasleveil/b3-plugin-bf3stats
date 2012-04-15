BF3stats plugin for Big Brother Bot (www.bigbrotherbot.net)
===========================================================


Description
-----------

This plugin provides a commands which can query the bf3stats.com website for stats about players.


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

This plugin has been make possible thanks to `Ozon's work <https://github.com/ozon/python-bf3stats>`_


Contrib
-------

- *features* can be discussed on the `B3 forums <http://bit.ly/HUCyw3>`_
- documented and reproducible *bugs* can be reported on the `issue tracker <https://github.com/courgette/b3-plugin-bf3stats/issues>`_
- *patches* are welcome. Send me a `pull request <http://help.github.com/send-pull-requests/>`_. It is best if your patch provides tests.

.. image:: https://secure.travis-ci.org/courgette/b3-plugin-bf3stats.png?branch=master
   :alt: Build Status
   :target: http://travis-ci.org/courgette/b3-plugin-bf3stats

RSSCat
======

RSSCat is an automatic torrent download and notifier.

Requirements
============

* MongoDB
* python-pymongo
* python-feedparser
* python-requests
* python-bittorrent
* python-configobj

On Ubuntu, just run

```bash
apt-get install mongodb-server mongodb-clients python-pymongo python-feedparser python-requests python-bittorrent python-configobj
```

RSSCat expects a MongoDB instance living on localhost. Installing the mongodb-server package achieves just that.

Developed / Tested on
=====================

* Ubuntu 12.04
* Ubuntu 13.04


Configuration
=============

RSSCat can be configured in two way:

Configuration file
------------------

By default, RSSCat will look for a configuration file called `rsscat.config` in its root folder. If it finds one, it will load all options within. To use this, simply copy `rsscat.config.default`, and edit accordingly.

To instead use a configuration file in another location, specify the `--config` option with the config file's absolute path.

CLI options
-----------

Every option specified on the CLI will override its counterpart configuration file option. That is, if you set `torrentdir=/some/dir`, and also specify `--torrentdir=/the/right/dir`, RSSCat will use the `/the/right/dir` as the torrentdir.

Run RSSCat with the `-h` or `--help` option to see all available CLI options.

Basic operation
===============

RSSCat has three distinct threads of execution:

1. It checks all configured RSS feeds for any new items, and stores them.
2. It checks if any of these new items have been processed before. If not, it will download the torrent file the specified torrentdir.
3. It checks if any recent processed items require a notification. This will only happen if a Pushover user key has been defined.

Defining new feeds
==================

RSSCat will look in the `feeds` collection, in the `rsscat` database for any feed that is enabled. For now, defining new feeds has to be done manually. This example uses the mongo cli tool provided by the mongodb-clients package.

```bash
$ mongo
MongoDB shell version: 2.2.4
connecting to: test
> use rsscat
switched to db rsscat
> db.feeds.insert({ "name": "My Torrent RSS feed", "url": "http://some.torrent.host/feed.xml", "enabled": true })
> exit
```

This can be done while RSSCat is still running. After this, RSSCat will automatically pick up the new feed, download it, and determine what items need processing (usually all of them).

Avoiding duplicates
===================

Because multiple RSS feeds can contain the same torrent files, RSSCat tries to avoid downloading duplicate torrent files. 

* When downloading new torrent files, it compares its info hash with all info hashes already known to RSSCat. If it finds that it has already downloaded it, it will mark it as duplicate and skip it in future runs.
* If the info hash is not a duplicate, but a file already exists with the exact same filename, it will mark it as error, and also skip it in future runs.

More checks may be added in the future if the need arises.

License
=======

RSSCat is licensed under the GPLv3 license.

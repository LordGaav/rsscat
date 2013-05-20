#!/usr/bin/env python
# Copyright (c) 2012 Nick Douma < n.douma [at] nekoconeko . nl >
# 
# This file is part of rsscat.
# 
# rsscat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# rsscat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with rsscat. If not, see <http://www.gnu.org/licenses/>.

import sys

if sys.version_info < (2, 7):
	print "Sorry, {0} requires Python 2.7.".format(rsscat.NAME)
	sys.exit(1)

import time, signal, os, inspect
import rsscat
from argparse import ArgumentParser
from configobj import ConfigObj

config_parser = ArgumentParser(description="Looking for config", add_help=False)
config_parser.add_argument('--config', metavar='CONFIG', type=str)

config_arg, config_unknown = config_parser.parse_known_args()

loc = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if config_arg.config:
	config = ConfigObj(config_arg.config)
elif os.path.isfile(os.path.join(loc, "rsscat.config")):
	config = ConfigObj(os.path.join(loc, "rsscat.config"))
else:
	config = ConfigObj()

arg_parser = ArgumentParser(description="{0} is an automatic torrent download and notifier".format(rsscat.NAME))
arg_parser.add_argument("--torrentdir", metavar="DIR", type=str, default=config.get("torrentdir", None), help="Where to save new torrents")
arg_parser.add_argument("--daemonize", action="store_true", default=config.as_bool("daemonize"), help="Fork to background")
arg_parser.add_argument("--uid", metavar="UID", type=str, default=config.get("uid", None), help="What user to fork as. Note: requires running {0} as root".format(rsscat.NAME))
arg_parser.add_argument("--gid", metavar="GID", type=str, default=config.get("gid", None), help="What group to fork as. Note: requires running {0} as root".format(rsscat.NAME))
arg_parser.add_argument("--pidfile", metavar="PID", type=str, default=config.get("pidfile", None), help="Where to save a PID file when forking")
arg_parser.add_argument("--logfile", metavar="LOG", type=str, default=config.get("logfile", None), help="Will save output to specified log file")
arg_parser.add_argument("--loglevel", metavar="LEVEL", type=str, default=config.get("loglevel", "INFO"), help="Minimum level message to log")
arg_parser.add_argument("--pushover_user_key", metavar="UKEY", type=str, default=config.get("pushover_user_key", None), help="What user to send Pushover notifications to")

args = arg_parser.parse_args()

log_handlers = {}
if args.logfile:
	log_handlers['file'] = { "logfile": args.logfile }
if not args.daemonize:
	log_handlers['console'] = None
logger = rsscat.getLogger("rsscat", level=args.loglevel, handlers=log_handlers)

if not args.torrentdir:
	logger.fatal("{0} requires a torrent dir to be set!".format(rsscat.NAME))
	sys.exit(1)
else:
	rsscat.TORRENTDIR = args.torrentdir

rsscat.DAEMON = args.daemonize
if args.uid:
	rsscat.SETUID = args.uid
if args.gid:
	rsscat.SETGID = args.gid
if args.pidfile:
	rsscat.CREATEPID = args.pidfile
if args.pushover_user_key:
	rsscat.PUSHOVER_USER_KEY = args.pushover_user_key

logger.info("{0} version {1} starting...".format(rsscat.NAME, rsscat.VERSION))

signal.signal(signal.SIGINT, rsscat.signal_handler)
signal.signal(signal.SIGTERM, rsscat.signal_handler)

def main():
	if rsscat.DAEMON:
		rsscat.daemonize()
	rsscat.initialize()
	rsscat.startAll()

	# Stay alive to handle signals
	while True:
		time.sleep(2)

if __name__ == "__main__":
	main()

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

import sys, logging, time, signal
import rsscat

logger = rsscat.getLogger("rsscat", level=logging.DEBUG, handlers={"console": None, "file": {"logfile": "test.log"}})
logger.info("{0} version {1} starting...".format(rsscat.NAME, rsscat.VERSION))

if sys.version_info < (2, 7):
	logger.error("Sorry, {0} requires Python 2.7.".format(rsscat.NAME))
	sys.exit(1)

signal.signal(signal.SIGINT, rsscat.signal_handler)
signal.signal(signal.SIGTERM, rsscat.signal_handler)

def main():
	rsscat.daemonize()
	rsscat.initialize()
	rsscat.startAll()

	# Stay alive to handle signals
	while (True):
		time.sleep(2)

if __name__ == "__main__":
	main()

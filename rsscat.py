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
import os
import logging
import rsscat

logger = rsscat.getLogger("rsscat", level=logging.DEBUG, handlers={"console": None, "file": {"logfile": "test.log"}})
logger.info("{0} version {1} starting...".format(rsscat.NAME, rsscat.VERSION))

if sys.version_info < (2, 7):
	logger.error("Sorry, {0} requires Python 2.7.".format(rsscat.NAME))
	sys.exit(1)

def daemonize():
	# Make a non-session-leader child process
	try:
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("First fork failed: %s [%d]" % (e.strerror, e.errno))

	os.setsid()

	# Make sure I can read my own files and shut out others
	prev = os.umask(0)
	os.umask(prev and int('077', 8))

	# Make the child a session-leader by detaching from the terminal
	try:
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("Second fork failed: %s [%d]" % (e.strerror, e.errno))

	dev_null = file('/dev/null', 'r')
	os.dup2(dev_null.fileno(), sys.stdin.fileno())

	if rsscat.CREATEPID:
		pid = str(os.getpid())
		logger.info("Writing PID {0} to {1}".format(pid, str(rsscat.PIDFILE)))
		file(rsscat.PIDFILE, 'w').write("%s\n" % pid)

	logger.info("Forked main worker into background...")

import pymongo
from rsscat import mongo, worker

def main():
	daemonize()
	mongo.prepare_database()
	rsscat.initialize()

if __name__ == "__main__":
	main()

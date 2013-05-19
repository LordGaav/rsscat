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
import sys, os, pwd, grp, logging
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
		raise RuntimeError("First fork failed: {0} [{1}]".format(e.strerror, e.errno))

	os.setsid()
	if os.getuid() == 0:
		if rsscat.SETGID:
			gid = grp.getgrnam(rsscat.SETGID).gr_gid
			os.setgid(gid)
		if rsscat.SETUID:
			uid = pwd.getpwnam(rsscat.SETUID).pw_uid
			os.setuid(uid)

	# Make sure I can read my own files and shut out others
	prev = os.umask(0)
	os.umask(prev and int('077', 8))

	# Make the child a session-leader by detaching from the terminal
	try:
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("Second fork failed: {0} [{1}]".format(e.strerror, e.errno))

	dev_null = file('/dev/null', 'r')
	os.dup2(dev_null.fileno(), sys.stdin.fileno())

	if rsscat.CREATEPID:
		try:
			pid = str(os.getpid())
			logger.info("Writing PID {0} to {1}".format(pid, str(rsscat.CREATEPID)))
			file(rsscat.CREATEPID, 'w').write("%s\n" % pid)
		except IOError, e:
			raise RuntimeError("Failed to create PID file: {0} [{1}]".format(e.strerror, e.errno))

	logger.info("Forked main worker into background...")


import pymongo, time, signal
from rsscat import mongo

signal.signal(signal.SIGINT, rsscat.signal_handler)
signal.signal(signal.SIGTERM, rsscat.signal_handler)

def main():
	daemonize()
	rsscat.initialize()
	rsscat.startAll()

	# Stay alive to handle signals
	while (True):
		time.sleep(2)

if __name__ == "__main__":
	main()

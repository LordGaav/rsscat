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

NAME = "RSSCat"
VERSION = "0.1"

DAEMON = False
CREATEPID = "rsscat.pid"

SETUID = None
SETGID = None

THREADS = None

TORRENTDIR = 'torrents'

PUSHOVER_USER_KEY = None

import logging, logging.handlers, os, pwd, grp, sys
from rsscat.threads import Threads
from rsscat.scheduler import Scheduler
from rsscat.downloader import downloadFeeds, downloadItems
from rsscat.pushover import pushover_notify

def getLogger(name, level=logging.INFO, handlers=[]):
	logger = logging.getLogger(name)

	if len(handlers) != 0:
		logger.setLevel(level)

	if "console" in handlers:
		strm = logging.StreamHandler()
		fmt = logging.Formatter('%(message)s')
		strm.setLevel(level)
		strm.setFormatter(fmt)
		logger.addHandler(strm)
	
	if "file" in handlers:
		conf = handlers['file']
		fl = logging.handlers.WatchedFileHandler(conf['logfile'])
		fl.setLevel(level)
		fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fl.setFormatter(fmt)
		logger.addHandler(fl)

	return logger

def hello(text):
	getLogger(__name__).info(text)

def daemonize():
	global SETGID, SETUID, CREATEPID

	# Make a non-session-leader child process
	try:
		pid = os.fork()
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("First fork failed: {0} [{1}]".format(e.strerror, e.errno))

	os.setsid()
	if os.getuid() == 0:
		if SETGID:
			gid = grp.getgrnam(SETGID).gr_gid
			os.setgid(gid)
		if SETUID:
			uid = pwd.getpwnam(SETUID).pw_uid
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

	if CREATEPID:
		try:
			pid = str(os.getpid())
			getLogger(__name__).info("Writing PID {0} to {1}".format(pid, str(CREATEPID)))
			file(CREATEPID, 'w').write("%s\n" % pid)
		except IOError, e:
			raise RuntimeError("Failed to create PID file: {0} [{1}]".format(e.strerror, e.errno))

	getLogger(__name__).info("Forked into background...")

def initialize():
	global THREADS

	getLogger(__name__).info("Initializing...")

	if THREADS is None:
		THREADS = Threads()

	updateThread = Scheduler(60, downloadFeeds, "UpdateThread", True)
	torrentThread = Scheduler(20, downloadItems, "TorrentThread", False)

	THREADS.registerThread("update", updateThread)
	THREADS.registerThread("torrent", torrentThread)

	if PUSHOVER_USER_KEY:
		notifyThread = Scheduler(20, pushover_notify, "NotifyThread", False)
		THREADS.registerThread("notify", notifyThread)

def startAll():
	global THREADS

	getLogger(__name__).info("Starting {0} threads...".format(NAME))

	for thread in THREADS.getThreads():
		t = THREADS.getThread(thread)
		getLogger(__name__).debug("Starting {0}".format(t.name))
		t.start()

	getLogger(__name__).info("Started all threads")

def stopAll():
	global THREADS, CREATEPID

	getLogger(__name__).info("Stopping {0} threads...".format(NAME))

	for thread in THREADS.getThreads():
		t = THREADS.getThread(thread)
		getLogger(__name__).info("Stopping {0}".format(t.name))
		t.stop = True
		t.join()
		THREADS.unregisterThread(thread)

	getLogger(__name__).info("Stopped all threads")
	getLogger(__name__).fatal("Comitting suicide")

	if DAEMON and CREATEPID:
		getLogger(__name__).info("Removing PID file")
		os.unlink(CREATEPID)

	os._exit(0)

def signal_handler(signum=None, frame=None):
	if type(signum) != type(None):
		getLogger(__name__).info("Caught signal {0}".format(signum))
		stopAll()

if __name__ == "__main__":
	getLogger(__name__, handlers=["console"]).fatal("This file should NOT be called directly!")

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
CREATEPID = True
PIDFILE = "rsscat.pid"
THREADS = None

import logging, logging.handlers, time, os
from rsscat.threads import Threads
from rsscat.scheduler import Scheduler

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

def initialize():
	global THREADS

	getLogger(__name__).info("Initializing...")

	if THREADS == None:
		THREADS = Threads()

	helloThread = Scheduler(5, hello, "HelloThread", 10, "Hello world!")

	THREADS.registerThread("hello", helloThread)
	THREADS.getThread("hello").start()

def stopAll():
	global THREADS

	getLogger(__name__).info("Stopping {0} threads...".format(NAME))

	for thread in THREADS.getThreads():
		t = THREADS.getThread(thread)
		getLogger(__name__).info("Stopping {0}".format(t.name))
		t.stop = True
		t.join()
		THREADS.unregisterThread(thread)

	getLogger(__name__).info("Stopped all threads")
	getLogger(__name__).fatal("Comitting suicide")

	os._exit(0)

def signal_handler(signum=None, frame=None):
	if type(signum) != type(None):
		getLogger(__name__).info("Caught signal {0}".format(signum))
		stopAll()

if __name__ == "__main__":
	getLogger(__name__, handlers=["console"]).fatal("This file should NOT be called directly!")

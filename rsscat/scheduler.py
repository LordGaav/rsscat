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

import rsscat
import threading
import datetime
import time

class Scheduler(threading.Thread):
	def __init__(self, delay, action, name, startNow=False, *args, **kwargs):
		self.logger = rsscat.getLogger("{0}.{1}".format(__name__, name))
		super(Scheduler, self).__init__(None, None, name, None, None)

		self.delay = delay
		self.action = action
		self.name = name
		self.args = args
		self.kwargs = kwargs

		self.stop = False
		if startNow == True:
			self.lastRun = datetime.datetime.min
			self.logger.debug("Thread {0} will start immediately".format(name))
		else:
			self.lastRun = datetime.datetime.now()
			if isinstance(startNow, (int, long)):
				self.lastRun = self.lastRun + datetime.timedelta(seconds=startNow)
			wait = (self.lastRun - datetime.datetime.now()).seconds + delay
			self.logger.debug("Thread {0} will start in {1} seconds".format(name, wait))

	def run(self):
		self.logger.debug("Thread {0} is entering main loop".format(self.name))
		while not self.stop:
			if (datetime.datetime.now() - self.lastRun).total_seconds() > self.delay:
				self.logger.debug("Thread {0} is running".format(self.name))
				self.action(*self.args, **self.kwargs)
				self.lastRun = datetime.datetime.now()
				self.logger.debug("Thread {0} is done".format(self.name))
			time.sleep(1)
		self.logger.debug("Thread {0} is exiting main loop".format(self.name))

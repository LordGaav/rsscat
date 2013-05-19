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
		self.main_action = action
		self.name = name
		self.main_args = args
		self.main_kwargs = kwargs

		self.stop = False
		now = datetime.datetime.now()
		if startNow == True:
			self.lastRun = datetime.datetime.min
			self.logger.debug("Thread {0} will start immediately".format(name))
		else:
			self.lastRun = now
			if isinstance(startNow, (int, long)):
				self.lastRun += datetime.timedelta(seconds=startNow)
			wait = (self.lastRun - now).seconds + delay
			self.logger.debug("Thread {0} will start in {1} seconds".format(name, wait))
	
	def setStartAction(self, action, *args, **kwargs):
		self.init_action = action
		self.init_args = args
		self.init_kwargs = kwargs
	
	def setStopAction(self, action, *args, **kwargs):
		self.stop_action = action
		self.stop_args = args
		self.stop_kwargs = kwargs

	def run(self):
		self.logger.debug("Thread {0} is entering main loop".format(self.name))

		if hasattr(self, "init_action"):
			self.logger.debug("Thread {0} is calling its init action")
			self.init_action(*self.init_args, **self.kwargs)

		while not self.stop:
			if (datetime.datetime.now() - self.lastRun).total_seconds() > self.delay:
				self.logger.debug("Thread {0} is running".format(self.name))
				try:
					self.main_action(*self.main_args, **self.main_kwargs)
				except Exception:
					self.logger.exception("Thread {0} generated an exception!".format(self.name))

				self.lastRun = datetime.datetime.now()
				self.logger.debug("Thread {0} is done".format(self.name))
			time.sleep(1)

		if hasattr(self, "stop_action"):
			self.logger.debug("Thread {0} is calling its stop action")
			self.stop_action(*self.stop_args, **self.stop_kwargs)

		self.logger.debug("Thread {0} is exiting main loop".format(self.name))

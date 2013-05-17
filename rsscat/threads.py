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

class Threads(object):
	thread_list = {}

	def __init__(self):
		self.logger = rsscat.getLogger(__name__)

	def registerThread(self, name, thread):
		if name in self.thread_list:
			self.logger.error("Thread {0} already registered!".format(name))
			raise Exception("Thread {0} already registered!".format(name))

		self.thread_list[name] = thread
		self.logger.debug("Registered thread {0}".format(name))
	
	def getThreads(self):
		return self.thread_list.keys()

	def getThread(self, name):
		if not name in self.thread_list:
			self.logger.error("Thread {0} is not registered!".format(name))
			raise Exception("Thread {0} is not registered!".format(name))

		return self.thread_list[name]

	def unregisterThread(self, name):
		if not name in self.thread_list:
			self.logger.error("Thread {0} is not registered!".format(name))
			raise Exception("Thread {0} is not registered!".format(name))

		del self.thread_list[name]
		self.logger.debug("Unregistered thread {0}".format(name))

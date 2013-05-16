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
from pymongo.connection import Connection

connection = Connection()
feeds_collection = None

def prepare_database():
	logger = rsscat.getLogger(__name__)
	logger.info("Preparing mongo database")
	db = connection['rsscat']
	feeds_collection = db['feeds']

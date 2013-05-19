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
from rsscat.mongo import get_collection
from rsscat.mongo import dbref as dbref
import threading, datetime, time
import feedparser

def downloadFeeds():
	logger = rsscat.getLogger("{0}.{1}".format(__name__, "downloadFeeds"))
	logger.info("FeedDownloader starting")

	col = get_collection('feeds')
	feeds = col.find({ "enabled": True })
	for feed in feeds:
		logger.debug("Processing feed {0}".format(feed['name']))
		processItems(feed)

	logger.info("FeedDownloader is finished")

def processItems(_feed):
	logger = rsscat.getLogger("{0}.{1}".format(__name__, "processItems"))
	feed = feedparser.parse(_feed['url'])

	if "title" in feed:
		logger.debug("Finding items for feed {0}".format(feed.title))
	else:
		logger.debug("Finding items for feed {0}".format(_feed['url']))
	logger.debug("This feed has {0} items".format(len(feed.entries)))

	col = get_collection('items')
	for entry in feed.entries:
		logger.debug("Processing entry {0}".format(entry.id))
		if col.find({ '_id': entry.id}).count() > 0:
			logger.debug("Entry already exists")
			continue

		if not "link" in entry:
			logger.debug("Entry does not have a link")
			continue

		entry_date = datetime.datetime.now()
		for field in [ 'published_parsed', 'created_parsed', 'updated_parsed', 'expired_parsed' ]:
			if field in entry:
				entry_date = getattr(entry, field)
				entry_date = datetime.datetime.fromtimestamp(time.mktime(entry_date))
				break

		item = {
			'_id': entry.id if "id" in entry else entry.link,
			'feed': dbref("feeds", _feed['_id']),
			'url': entry.link,
			'date': entry_date,
			'processed': False
		}

		col.insert(item)
		logger.info("Inserted new item for feed {0}: {1}".format(_feed['name'], item['_id']))


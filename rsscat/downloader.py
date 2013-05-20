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
import datetime, time, os, hashlib
import feedparser
import requests
import urlparse
import BitTorrent.bencode

def downloadFeeds():
	logger = rsscat.getLogger("{0}.{1}".format(__name__, "downloadFeeds"))
	logger.debug("FeedDownloader starting")

	col = get_collection('feeds')
	feeds = col.find({ "enabled": True })
	for feed in feeds:
		logger.debug("Processing feed {0}".format(feed['name']))
		processItems(feed)

	logger.debug("FeedDownloader is finished")

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
			'title': entry.title if "title" in entry else entry.link,
			'url': entry.link,
			'date': entry_date,
			'status': 'new'
		}

		col.insert(item)
		logger.info("Inserted new item for feed {0}: {1}".format(_feed['name'], item['_id']))

def downloadItems():
	logger = rsscat.getLogger("{0}.{1}".format(__name__, "downloadItems"))
	col = get_collection('items')
	items = col.find({ 'status': 'new' })

	if items.count() == 0:
		logger.debug("No new items found to download")
		return

	if not os.path.exists(rsscat.TORRENTDIR):
		try:
			os.mkdir(rsscat.TORRENTDIR)
		except OSError:
			logger.exception("Failed to create TORRENTDIR")
			return

	for item in items:
		logger.debug("Processing new item: {0}".format(item['title']))

		req = requests.get(item['url'])
		if "content-disposition" in req.headers and req.headers['content-disposition'].find('filename=') != -1:
			filename = req.headers['content-disposition'].split("filename=")[1].replace("\"", "")
		else:
			dis = urlparse.urlparse(item['url'])
			filename, ext = os.path.splitext(os.path.basename(dis.path))
			if ext == ".torrent":
				filename = filename + ext

		raw_torrent = req.content
		try:
			torrent = BitTorrent.bencode.bdecode(raw_torrent)
		except ValueError:
			logger.exception("Failed to decode torrent for {0}".format(item['url']))
			continue

		info_hash = _get_info_hash(torrent['info'])
		if filename is None:
			filename = "{0}.torrent".format(info_hash)

		if col.find({ 'info-hash': info_hash}).count() > 0:
			logger.warning(("A torrent for INFO HASH {0} has already been processed, skipping {1}".format(info_hash, filename)))
			col.update({ "_id": item['_id'] }, { '$set': { 'status': 'duplicate' } })
			continue

		col.update({ "_id": item['_id'] }, { '$set': { 'info-hash': info_hash } })

		if os.path.exists(os.path.join(rsscat.TORRENTDIR, filename)):
			logger.debug("File already exists, skipping")
			col.update({ "_id": item['_id'] }, { '$set': { 'status': 'error' } })
			continue

		try:
			out = open(os.path.join(rsscat.TORRENTDIR, filename), "w")
			out.write(raw_torrent)
			out.close()
		except OSError:
			logger.exception("Failed to write torrent file {0} to disk".format(filename))
			col.update({ "_id": item['_id'] }, { '$set': { 'status': 'error' } })
			continue

		col.update({ "_id": item['_id'] }, { '$set': { 'status': 'processed' } })

def _get_info_hash(info):
	sha = hashlib.sha1()
	sha.update(BitTorrent.bencode.bencode(info))

	return sha.hexdigest()
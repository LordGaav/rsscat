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

PUSHOVER_APP_KEY = 'BchGiiKGt8yqMGbUtto9xoH1vGsz3e'
PUSHOVER_API_URL = 'https://api.pushover.net/1/messages.json'

import rsscat
from rsscat.mongo import get_collection
import requests, datetime

def pushover_notify(items=None):
	logger = rsscat.getLogger("{0}.{1}".format(__name__, "pushover_notify"))
	col = get_collection("items")

	date_cutoff = datetime.datetime.now() - datetime.timedelta(days=1)

	if not isinstance(items, list):
		items = col.find({ "date": { "$gte": date_cutoff }, "notifications.pushover": { "$not": { "$exists": True } }  })

		if items.count() == 0:
			logger.debug("No notifications need sending")
			return
	elif len(items) == 0:
		logger.debug("No notifications need sending")
		return

	for item in items:
		message = {
			"token": PUSHOVER_APP_KEY,
		    "user": rsscat.PUSHOVER_USER_KEY,
		    "message": "Processed item {0}".format(item['title'])
		}

		response = requests.post(PUSHOVER_API_URL, message)

		message['date'] = datetime.datetime.now()
		del message['token']
		del message['user']

		if response.status_code != requests.codes.ok:
			message['status'] = "failed"
			logger.error("Failed to send Pushover notification for {0}".format(item['title']))
			logger.error(response.text)
		else:
			message['status'] = "ok"
			logger.info("Sent Pushover notification for {0}".format(item['title']))

		col.update({ "_id": item['_id']}, { "$set": { "notifications.pusover": message } })

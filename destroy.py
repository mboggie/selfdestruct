# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twitter import *
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os

jargonlist = ["longing for", "yearning for"]

try:
	authblock = OAuth(
	    consumer_key = os.environ["SDAPP_CONSUMER_KEY"],
	    consumer_secret = os.environ["SDAPP_CONSUMER_SECRET"],
	    # in future tokens will be addressed programmatically; this is just for now
	    token = os.environ["SDAPP_ACCESS_KEY"],
	    token_secret = os.environ["SDAPP_ACCESS_SECRET"]
	)

except KeyError:
	print "Please set your \"SDAPP_\" environment variables for Twitter OAuth before running destroy.py."

def schedule(tweet):
	#simple case: we did the search on SD5 first. start there.
	
	createstring = tweet['created_at']
	createtime = parse(createstring)
	destroytime = createtime + timedelta(0,5*60)

	#schedule destruction at destroytime

	print "%s wants to destroy a tweet at  %s: \n\"%s\"" % (tweet['user']['screen_name'], dt.strftime(destroytime, "%c"), tweet['text'])
	
#end schedule 

if __name__ == "__main__":
	t = Twitter(auth=authblock)
	search_results = t.search.tweets(q="#sd5")

	for tweet in search_results['statuses']:
		schedule(tweet)
		
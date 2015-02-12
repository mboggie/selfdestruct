# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twython import Twython
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os, sys, json, time, string, re
import urllib, httplib, base64
import beanstalkc
import redis

# Default TTL = how long an #SD tweet lasts if no number of minutes has been specified
DEFAULT_TTL = 5
DEFAULT_SINCE_ID = 240859602684612608 #random, yet valid, id from 2012. Twitter doesn't like it if you just pass 0.

try:
	
    CONSUMER_KEY = os.environ["SDAPP_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["SDAPP_CONSUMER_SECRET"]
    BEANSTALK_HOST = os.environ["SDAPP_BEANSTALK_HOST"]
    BEANSTALK_PORT = int(os.environ["SDAPP_BEANSTALK_PORT"])
    BEANSTALK_TUBE = os.environ["SDAPP_BEANSTALK_TUBE"]
    REDIS_HOST = os.environ["SDAPP_REDIS_HOST"]
    REDIS_PORT = int(os.environ["SDAPP_REDIS_PORT"])

except KeyError:
	print "Please set your \"SDAPP_\" environment variables for Twitter OAuth before running destroy-mon.py."
	sys.exit(2)

#print (BEANSTALK_HOST + ":" + str(BEANSTALK_PORT))
beanstalk = beanstalkc.Connection(host=BEANSTALK_HOST, port=BEANSTALK_PORT)
beanstalk.connect()

# use tube to place tweets for destruction
beanstalk.use(BEANSTALK_TUBE)

#connect to redis
rserver = redis.Redis(REDIS_HOST, REDIS_PORT)


def schedule(tweet):
	
	#find the offset required
	searchresult = re.search("#sd(\d+)", tweet['text'])
	if searchresult: 
		ttl = searchresult.group(1)
		if len(ttl) > 0:
			ttl = int(ttl)
		else:
			ttl = DEFAULT_TTL
 	else:
 		ttl = DEFAULT_TTL
	#schedule destruction at destroytime

	# right / hard way: two date comparisons that respect timezone
	# NOTE: Twitter "created_at" attribute is always in UTC
	# createstring = tweet['created_at']
	# createtime = parse(createstring)
	# destroytime = createtime + timedelta(0,ttl*60)
	# #finish calculations here because python sucks at timezone

	#lazy way: ttl*60seconds = beanstalk delay
	destroytime = ttl*60

	print "[destroy-mon] %s wants to destroy a tweet in %s min: \n\"%s\"" % (tweet['user']['screen_name'], destroytime, tweet['id'])

	job = {}
	job['id'] = tweet['id']
	job['screen_name'] = tweet['user']['screen_name']

	beanstalk.put(json.dumps(job), delay=destroytime)

#end schedule 

if __name__ == "__main__":

	#connect to Twitter
	# t = Twython(CONSUMER_KEY, CONSUMER_SECRET, oauth_version=2)
	# authtoken = t.obtain_access_token()
	# t = Twython(CONSUMER_KEY, access_token=authtoken)

	#get list of subscribers
	userlist = rserver.lrange("users", 0, rserver.llen("users"))
	
	#begin loop
	for screen_name in userlist:
		#in this area, add try/except areas for db calls and for Twitter info
		since_id = rserver.get("since_id:"+screen_name)
		if since_id is None:
			since_id = DEFAULT_SINCE_ID
		else:
			since_id = long(since_id)
		creds = rserver.get("credentials:"+screen_name)
		creds = json.loads(creds)
		# connect to Twitter with keys for each individual user
		t = Twython(CONSUMER_KEY, CONSUMER_SECRET, creds["token"], creds["secret"])
		
		#for each user who has signed up, retrieve all tweets from user since last we checked
		tweets =t.get_user_timeline(screen_name=screen_name, since_id=since_id)
		print "%d tweets received for %s" % (len(tweets), screen_name)

		for tweet in tweets:	
			# 	see if this tweet has been marked to selfdestruct
			print tweet['id']
			status = string.find(string.lower(tweet['text']), "#sd")
			if status > 0:
				schedule(tweet)

			#	reset this user's pointer so future calls don't return tweets we've already seen
			if tweet['id'] > since_id:
				rserver.set("since_id:"+screen_name, tweet['id'])
				since_id = tweet['id']
				print("setting since_id to " + str(tweet['id']))
		#end inner for
	#end outer for
#end

		
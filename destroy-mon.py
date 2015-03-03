# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twython import Twython, TwythonAuthError
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os, sys, json, time, string, re
import urllib, httplib, base64
import beanstalkc
import redis
import argparse
import ConfigParser

# Default TTL = how long an #SD tweet lasts if no number of minutes has been specified
DEFAULT_TTL = 5
DEFAULT_SINCE_ID = 240859602684612608 #random, yet valid, id from 2012. Twitter doesn't like it if you just pass 0.

# parse arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('config', help='path to config file')
args = argparser.parse_args()


# read application config
cfg = ConfigParser.ConfigParser()
cfg.read(args.config)

try:
	
    CONSUMER_KEY = cfg.get('twitter', 'app_key')
    CONSUMER_SECRET = cfg.get('twitter', 'app_secret')
    BEANSTALK_HOST = cfg.get('beanstalk', 'host')
    BEANSTALK_PORT = int(cfg.get('beanstalk', 'port'))
    BEANSTALK_TUBE = cfg.get('beanstalk', 'tube')
    REDIS_HOST = cfg.get('redis', 'host')
    REDIS_PORT = int(cfg.get('redis', 'port'))

except:
	print "Please set your config variables properly in %s before running destroy-mon.py." %args.config
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

	print "[destroy-mon] %s wants to destroy a tweet in %s sec: \n\"%s\"" % (tweet['user']['screen_name'], destroytime, tweet['id'])

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
	print userlist

	#begin loop
	for screen_name in userlist:
		print "Checking timeline for user %s"%screen_name
		#in this area, add try/except areas for db calls and for Twitter info
		since_id = rserver.get("since_id:"+screen_name)
		if since_id is None:
			since_id = DEFAULT_SINCE_ID
		else:
			since_id = long(since_id)
		creds = rserver.get("credentials:"+screen_name)
		if creds is None:
			print "%s has revoked access"%screen_name
		else:
			creds = json.loads(creds)
			# connect to Twitter with keys for each individual user
			try:
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
			
			except TwythonAuthError:
				# user has revoked access; mark them as disabled and move on
				rserver.delete("credentials:"+screen_name)
				rserver.lrem("users", screen_name, 0)
	#end outer for
#end

		
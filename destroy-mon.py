# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twitter import *
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os, sys, json, time, string, re
import urllib, httplib, base64
import beanstalkc

# Default TTL = how long an #SD tweet lasts if no number of minutes has been specified
DEFAULT_TTL = 0.1

try:
	
    CONSUMER_KEY = os.environ["SDAPP_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["SDAPP_CONSUMER_SECRET"]
    BEANSTALK_HOST = os.environ["SDAPP_BEANSTALK_HOST"]
    BEANSTALK_PORT = int(os.environ["SDAPP_BEANSTALK_PORT"])
    BEANSTALK_TUBE = os.environ["SDAPP_BEANSTALK_TUBE"]
    # in future tokens will be addressed programmatically; this is just for now
    # token = os.environ["SDAPP_ACCESS_KEY"],
    # token_secret = os.environ["SDAPP_ACCESS_SECRET"]

except KeyError:
	print "Please set your \"SDAPP_\" environment variables for Twitter OAuth before running destroy-mon.py."
	sys.exit(2)

print BEANSTALK_PORT
beanstalk = beanstalkc.Connection(host=BEANSTALK_HOST, port=BEANSTALK_PORT)
beanstalk.connect()

# use tube to place tweets for destruction
beanstalk.use(BEANSTALK_TUBE)

def getTwitterAppOauth():
	encoded_CONSUMER_KEY = urllib.quote(CONSUMER_KEY)
	encoded_CONSUMER_SECRET = urllib.quote(CONSUMER_SECRET)

	concat_consumer_url = encoded_CONSUMER_KEY + ":" + encoded_CONSUMER_SECRET

	host = 'api.twitter.com'
	url = '/oauth2/token/'
	params = urllib.urlencode({'grant_type' : 'client_credentials'})
	req = httplib.HTTPSConnection(host)
	req.putrequest("POST", url)
	req.putheader("Host", host)
	req.putheader("User-Agent", "Python 2.7 / Twitter 1.1")
	req.putheader("Authorization", "Basic %s" % base64.b64encode(concat_consumer_url))
	req.putheader("Content-Type" ,"application/x-www-form-urlencoded;charset=UTF-8")
	req.putheader("Content-Length", "29")
	#req.putheader("Accept-Encoding", "gzip")

	req.endheaders()
	req.send(params)

	resp = req.getresponse()
	print resp.status, resp.reason
	bearer_token = json.loads(resp.read())
	if bearer_token['token_type'] == "bearer":
		return urllib.unquote(bearer_token['access_token']).decode('utf-8')
	else:
		raise ValueError("Expected bearer token from twitter oauth, received %s", bearer_token['token_type'])

#end getTwitterAppOauth

def schedule(tweet, authtoken):
	
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

	#right / hard way: two date comparisons that respect timezone
	# NOTE: Twitter "created_at" attribute is always in UTC
	# createstring = tweet['created_at']
	# createtime = parse(createstring)
	# destroytime = createtime + timedelta(0,ttl*60)
	# #finish calculations here because python sucks at timezone

	#lazy way: ttl*60seconds = beanstalk delay
	destroytime = ttl*60
	print "[destroy-mon] %s wants to destroy a tweet in %s min: \n\"%s\"" % (tweet['user']['screen_name'], destroytime, tweet['id'])
	job = {}
	# PUT IN REDIS HERE
	job['usertoken'] = AAA
	job['usersecret'] = BBB
	job['id'] = tweet['id']
	job['screen_name'] = tweet['user']['screen_name']

	# kludge to make unicode string a string string that beanstalk likes. NEED TO FIX FOR REAL 
	beanstalk.put(json.dumps(job), delay=destroytime)

#end schedule 

if __name__ == "__main__":
	#initialize our authorization as an application
	authtoken = getTwitterAppOauth()

	#connect to Twitter
	t = Twitter(auth=OAuth2(bearer_token=authtoken))

	#begin loop
	sinceid = 240859602684612608 #random, yet valid, id from 2012. Twitter doesn't like it if you just pass 0.

	#this will be a while loop later
	for i in range(0, 5):

		#for each user who has signed up
		#retrieve all tweets from user since last we checked
		tweets = t.statuses.user_timeline(screen_name="mattboggie", since_id=sinceid)
		print "%d run; %d tweets received" % (i,len(tweets))

	#analyze 
		for tweet in tweets:	
			# 	see if this tweet has been marked to selfdestruct
			status = string.find(string.lower(tweet['text']), "#sd")
			if status > 0:
				schedule(tweet, authtoken)

			#	reset this user's pointer so future calls don't return tweets we've already seen
			if tweet['id'] > sinceid:
				sinceid = tweet['id']

			schedule(tweet, authtoken)

		# only check our userlist once each minute
		time.sleep(60)
		#end inner for
	#end outer for
#end

		
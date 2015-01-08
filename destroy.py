# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twitter import *
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os, sys, json, time
import urllib, httplib, base64

jargonlist = ["longing for", "yearning for"]

try:
	
    CONSUMER_KEY = os.environ["SDAPP_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["SDAPP_CONSUMER_SECRET"]
    # in future tokens will be addressed programmatically; this is just for now
    # token = os.environ["SDAPP_ACCESS_KEY"],
    # token_secret = os.environ["SDAPP_ACCESS_SECRET"]

except KeyError:
	print "Please set your \"SDAPP_\" environment variables for Twitter OAuth before running destroy.py."
	sys.exit(2)

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
		return bearer_token['access_token']
	else:
		raise ValueError("Expected bearer token from twitter oauth, received %s", bearer_token['token_type'])

#end getTwitterAppOauth

def schedule(tweet):
	#simple case: we did the search on SD5 first. start there.
	
	createstring = tweet['created_at']
	createtime = parse(createstring)
	destroytime = createtime + timedelta(0,5*60)

	#schedule destruction at destroytime

	print "%s wants to destroy a tweet at  %s: \n\"%s\"" % (tweet['user']['screen_name'], dt.strftime(destroytime, "%c"), tweet['text'])
	
#end schedule 

if __name__ == "__main__":
	#initialize our authorization as an application
	authtoken = getTwitterAppOauth()
	authtoken = urllib.unquote(authtoken).decode('utf-8')

	#connect to Twitter
	t = Twitter(auth=OAuth2(bearer_token=authtoken))

	#begin loop
	sinceid = 240859602684612608
	for i in range(0, 5):

		#retrieve all tweets from user since last we checked
		tweets = t.statuses.user_timeline(screen_name="nytimes", since_id=sinceid)
		print "%d run; %d tweets received" % (i,len(tweets))

	#analyze 
		for tweet in tweets:
		# 	schedule(tweet)
			print tweet['text']
			if tweet['id'] > sinceid:
				sinceid = tweet['id']
				print sinceid
		time.sleep(30)
		#end inner for
	#end outer for
#end

		
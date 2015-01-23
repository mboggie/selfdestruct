# -*- coding: utf-8 -*-
from twython import Twython
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os, sys, json, time, string, re
import urllib, httplib, base64
import beanstalkc
import redis

try:
	
    CONSUMER_KEY = os.environ["SDAPP_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["SDAPP_CONSUMER_SECRET"]
    BEANSTALK_HOST = os.environ["SDAPP_BEANSTALK_HOST"]
    BEANSTALK_PORT = int(os.environ["SDAPP_BEANSTALK_PORT"])
    BEANSTALK_TUBE = os.environ["SDAPP_BEANSTALK_TUBE"]
    REDIS_HOST = os.environ["SDAPP_REDIS_HOST"]
    REDIS_PORT = int(os.environ["SDAPP_REDIS_PORT"])

except KeyError:
	print "Please set your \"SDAPP_\" environment variables for Twitter OAuth before running destroy-job.py."
	sys.exit(2)

beanstalk = beanstalkc.Connection(host=BEANSTALK_HOST, port=BEANSTALK_PORT)
beanstalk.connect()
beanstalk.watch(BEANSTALK_TUBE)

#connect to redis
rserver = redis.Redis(REDIS_HOST, REDIS_PORT)

while True:
    job = beanstalk.reserve()
    jobstr = job.body
    #print jobstr
    job.delete()
    tweet = json.loads(jobstr)

    #job will consist of tweet[id] and tweet[screenname] -- need to retrieve token and secret from redis
    cred = rserve.get("credentials:"+tweet['screen_name'])

	t = Twython(CONSUMER_KEY, CONSUMER_SECRET, cred['token'], cred['secret'])
    t.destroy_status(tweet['id'])

    #INCREMENT COUNT IN REDIS
    rserve.incr("deletecount:"+tweet['screen_name'], 1)


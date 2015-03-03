# -*- coding: utf-8 -*-
from twython import Twython, TwythonAuthError
from datetime import datetime as dt, timedelta
from dateutil.parser import parse
import os, sys, json, time, string, re
import urllib, httplib, base64
import beanstalkc
import redis
import argparse
import ConfigParser

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

except KeyError:
    print "Please set your config variables properly in %s before running destroy-job.py." %args.config
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
    cred = rserver.get("credentials:"+tweet['screen_name'])
    cred = json.loads(cred)

    try:
        t = Twython(CONSUMER_KEY, CONSUMER_SECRET, cred['token'], cred['secret'])
        t.destroy_status(id=tweet['id'])

        #INCREMENT COUNT IN REDIS
        print ("deleted tweet "+ str(tweet['id']))
        rserver.incr("deletecount:"+tweet['screen_name'], 1)
    except TwythonAuthError:
        # user has revoked access; mark them as disabled and move on
        rserver.delete("credentials:"+screen_name)
        rserver.lrem("users", screen_name, 0)

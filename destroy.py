# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twitter import *
import datetime

jargonlist = ["longing for", "yearning for"]

def schedule(status):
	#simple case: we did the search on SD5 first. start there.
	
	createtime = datetime.strptime(status['createdat'])
	destroytime = createtime + datetime.timedelta(0,5*60)

	#schedule destruction at destroytime

	print "%s wants to destroy a tweet at  %Z: \n\"%s\"" % (status['user']['screen_name'], destroytime, status['text'])
	
#end schedule 

if __name__ == "__main__":
	t = Twitter(auth=UserPassAuth("jargonjar", "abcdefg"))
	iterator = t.search.tweets(q="#sd5")

	for tweet in iterator:
		schedule(tweet)

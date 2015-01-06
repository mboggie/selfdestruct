# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.
# Note: Refactoring to use the better-maintained Python Twitter Tools APIs and hooks (https://github.com/sixohsix/twitter)

from twitter import *

#jargonlist = ["touch base"," productize", "table stakes", "game changer", "action item", "take this offline", "time box", "methodology", "solomo", "circle back", "the ask", "creatives", "gamify", "digital space", "mobile space", "plus up", "gamification"]

jargonlist = ["longing for", "yearning for"]

def parse_for_jargon(status):
	keyword = None

	if 'text' in status:
		for word in jargonlist:
			if word in status['text'].lower():
				keyword = word
		
		if keyword is None:
			#print "bzz"
			return
					
		# check if this is a straight RT; if so, skip it
		# check for special cases / regex matches for the word that disqualify it (i.e. "the asking")
		# insert the user / word if they don't exist, or...
		# update the count if they do

		print "%s said \"%s\" in %s" % (status['user']['screen_name'], keyword, status['text'])
	
#end 

if __name__ == "__main__":
	twitter_stream = TwitterStream(auth=UserPassAuth("jargonjar", "coldFus10n"))
	iterator = twitter_stream.statuses.sample()
	for tweet in iterator:
		parse_for_jargon(tweet)

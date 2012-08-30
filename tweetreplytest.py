# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.

import twitstream

jargonlist = ["gamify", "digital space", "mobile space", "plus up", "gamification"]

def callback(status):
	keyword = None
	for word in jargonlist:
		if word in status.get("text").lower():
			keyword = word
	
	if keyword is None:
		print "False positive, due to Twitter not honoring spaces."
		return
				
	print "%s said a jargon word! (%s) in %s" % (status.get('user', {}).get('screen_name'), keyword, status.get("text"))
#end 


twitstream.track("mattboggie", "5631jb", callback, jargonlist).run()
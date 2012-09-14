# -*- coding: utf-8 -*-
# May or may not need that up there, just saving it so I know what to do if I ever need unicode or something crazy.

import twitstream

jargonlist = ["touch base"," productize", "table stakes", "game changer", "action item", "take this offline", "time box", "methodology", "solomo", "circle back", "the ask", "creatives", "gamify", "digital space", "mobile space", "plus up", "gamification"]

def callback(status):
	keyword = None
	for word in jargonlist:
		if word in status.get("text").lower():
			keyword = word
	
	if keyword is None:
		return
				
	#check if this is a straight RT; if so, skip it
	#check for special cases / regex matches for the word that disqualify it (i.e. "the asking")
	#insert the user / word if they don't exist, or...
	#update the count if they do
	
	
	print "%s said a jargon word! (%s) in %s" % (status.get('user', {}).get('screen_name'), keyword, status.get("text"))
	



#end 


twitstream.track("jargonjar", "coldFus10n", callback, jargonlist).run()
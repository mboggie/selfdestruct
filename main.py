# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import tornado.gen
import Twython
import tornadoredis
import redis

class Status(tornado.web.RequestHandler):
	def get(self):

		user_key = self.get_secure_cookie('selfdestruct')

        if not user_key:
            self.redirect("/")
            return
        try:
            cookie = json.loads(user_key)
            screen_name = cookie["screen_name"]
        except:
            #doublecheck the cookie isn't hosed
            #if it is, kill it and have the user come back thru the oauth process
            self.clear_cookie('selfdestruct')
            self.redirect("/")
            return
        count = rserver.get("deletecount:"+screen_name)
		#tk: show stats of what's been deleted, what's queued, etc
		#for now, just render a "yeah, I know you" page
		self.render("status.html", count=count, screen_name=screen_name)

class LoginSuccess(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        oauth_verifier = self.get_argument('oauth_verifier')
        oauth_token = self.get_argument('oauth_token')
        secret = self.get_secure_cookie("sd_auth_secret")
        twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, oauth_token, secret)
        final_step = twitter.get_authorized_tokens(oauth_verifier)
        screen_name = final_step['screen_name']
        credentials = {}
        credentials['token'] = final_step['oauth_token']
        credentials['secret'] = final_step['oauth_token_secret']
        #save login info
        yield tornado.gen.Task(conn.set, "credentials:"+screen_name, json.dumps(credentials))
        yield tornado.gen.Task(conn.lpush, "users", screen_name)
        #set cookie
        cookie_data = {"token": final_step['oauth_token'], "secret": final_step['oauth_token_secret'], "screen_name": screen_name}
        self.set_secure_cookie("selfdestruct", json.dumps(cookie_data))
        self.clear_cookie("sd_auth_token")
        self.clear_cookie("sd_auth_secret")
        self.redirect("/status")

class TwitterLoginHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie('selfdestruct'):
            twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET)
            auth = twitter.get_authentication_tokens(callback_url= SDHOST+'/success')
            oauth_token = auth['oauth_token']
            oauth_token_secret = auth['oauth_token_secret']
            self.set_secure_cookie("sd_auth_token",oauth_token)
            self.set_secure_cookie("sd_auth_secret",oauth_token_secret)
            self.redirect(auth['auth_url'])
        else:
            self.redirect('/status')

class About(tornado.web.RequestHandler):
	def get(self):
		self.render("about.html")

class Intro(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie('selfdestruct'):
            self.render("intro.html")
        else:
            self.redirect('/status')


###################################################

try:	
    CONSUMER_KEY = os.environ["SDAPP_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["SDAPP_CONSUMER_KEY"]
   	SDHOST = os.environ["SDAPP_HOST"]
   	SDPORT = os.environ["SDAPP_PORT"]    
    REDIS_HOST = os.environ["SDAPP_REDIS_HOST"]
    REDIS_PORT = int(os.environ["SDAPP_REDIS_PORT"])

except KeyError:
	print "Please set your \"SDAPP_\" environment variables for Twitter OAuth before running main.py."
	sys.exit(2)

conn = tornadoredis.Client(host=REDIS_HOST, port=REDIS_PORT)
conn.connect()
rserver = redis.Redis(REDIS_HOST, REDIS_PORT)

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret="delete-my-tw33ts",
    twitter_consumer_key=CONSUMER_KEY,
    twitter_consumer_secret=CONSUMER_SECRET,
    debug=True
)

application = tornado.web.Application([
    (r"/", Intro),
    (r"/login", TwitterLoginHandler),
    (r"/success", LoginSuccess),
    (r"/status", Status)
    (r"/cancel", Cancel)
], **settings)

if __name__ == "__main__":
	#schedule the listener - it will be responsible for setting queues up and starting schedulers 

	#start tornado listener for web interface
    application.listen(SDPORT)
    logger.info("Selfdestruct Logger Inner starting on port %s" %SDPORT)
    tornado.ioloop.IOLoop.instance().start()


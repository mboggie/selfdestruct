# Self-destructing Tweets

A service that will monitor authenticated tweet streams and destroy tweets on your behalf

## Status

Once properly installed and configured, tweets will be reliably deleted. Most cases of error and exception have been handled and tested. Optimizations, including temporary suspension, will follow at a later time. Pull requests are welcome.

## Requirements

- Uses the Twython library for Twitter authentication
- Uses Redis to store user credentials and count tweets it's deleted
- Uses beanstalk to schedule deletion using the `delay` parameter for each job 
- Expects you to have saved a local config file (.cfg) with consumer tokens, beanstalk and redis ports, etc. (use sample.cfg as a guide)
- Consists of 3 processes:
	- `main.py`: Hosts the web front-end for Twitter OAuth, and for viewing deletion statuses
	- `destroy-mon.py`: For each OAuthed user, checks their stream for tweets containing "#sd" (must be scheduled using cron or other means: see `startup.sh`)
	- `destroy-job.py`: Pulls tweets ready to be deleted from the beanstalk queue and deletes them using the Twitter API


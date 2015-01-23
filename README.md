# Self-destructing Tweets

A service that will monitor authenticated tweet streams and destroy tweets on your behalf

## Status

This service is under development and does not currently work. Come back later.

## Requirements

- Uses the Twython library
- Uses Redis to store user credentials and count tweets it's deleted 
- Expects you to have saved a local secrets.sh with consumer tokens, beanstalk and redis ports, etc. and to have added that to the server's environment (use secrets_sample.sh as a guide)


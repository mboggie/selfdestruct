# import secrets into our environment
source secrets.sh

# startup redis
redis-server --port $SDAPP_REDIS_PORT &

# start beanstalk
beanstalkd -l $SDAPP_BEANSTALK_HOST -p $SDAPP_BEANSTALK_PORT &

# start oauth server/UI
python main.py >> sdmain.log 2>&1 &

# start destructor
python destroy-job.py >> sdjob.log 2>&1 &

# run monitor loop
while true
do 
	python destroy-mon.py >> sdmon.log 2>&1
	sleep 30
done

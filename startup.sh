# startup redis
# redis-server --port $SDAPP_REDIS_PORT &

# start beanstalk
# beanstalkd -l $SDAPP_BEANSTALK_HOST -p $SDAPP_BEANSTALK_PORT &

# start oauth server/UI
#python main.py selfdestruct.cfg >> sdmain.log 2>&1 &
python main.py selfdestruct.cfg &


# start destructor
#python destroy-job.py selfdestruct.cfg >> sdjob.log 2>&1 &
python destroy-job.py selfdestruct.cfg &

# run monitor loop
while true
do 
#	python destroy-mon.py selfdestruct.cfg >> sdmon.log 2>&1
	python destroy-mon.py selfdestruct.cfg &

	sleep 30
done

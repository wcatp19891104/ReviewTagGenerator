#!/usr/bin/env bash
d=$(screen -ls | grep -i backend-api | cut -d . -f 1)
screen -r $d
pwd
#cd bin
d=`diff -arq backend-api backend-api-temp --exclude=*.pyc --exclude=automatic_tool`
echo $d
cd ~
#d=$(diff -arq back-api backend-api-temp --exclude=*.pyc)
if ["$d" = ""]; then
    echo "no change detected, keep running"
else
	echo "different found, restart service"
	pwd
	cd bin/backend-api-temp
	pwd
	sudo chmod u+x restart.sh
	sudo chmod u+x stopserver.sh
	sudo chmod u+x startserver.sh
	sudo ./stopserver.sh
	cd ~
	cd bin/
	sudo rm -r backend-api
	cp -avr backend-api-temp/. backend-api/
	cd backend-api
	source ../../python_env/backend-api/bin/activate
	pip install -r requirements.txt
	#which python
	cd src
	cd API
	python analyzer_api.py &
	sleep 15
	python autocomplete.py &
	sleep 10
	python PriceLookup.py &
	sleep 10
	deactivate
fi;

pid=$(sudo lsof -i:8082 -t)
if [ "$pid" = "" ]; then
	echo "no instance running"
	cd ~
	cd bin/
	cd backend-api
	source ../../python_env/backend-api/bin/activate
	pip install -r requirements.txt
	#which python
	cd src
	cd API
	python analyzer_api.py &
	sleep 15
	python autocomplete.py &
	sleep 10
	python PriceLookup.py &
	sleep 10
	deactivate
else
	echo "instance is running"
fi
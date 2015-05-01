#!/bin/bash
pid=$(lsof -i:8082 -t); kill -TERM $pid || kill -KILL $pid
p=$(lsof -i:8108 -t); kill -TERM $p || kill -KILL $p
p3=$(lsof -i:8109 -t); kill -TERM $p3 || kill -KILL $p3
#cd backend-api
cd src
cd API

python analyzer_api.py &
sleep 15
python autocomplete.py &
sleep 10
python PriceLookup.py &
sleep 10

#!/bin/bash
cd src
cd API

python analyzer_api.py &
sleep 15
python autocomplete.py &
sleep 10
python PriceLookup.py &
sleep 10
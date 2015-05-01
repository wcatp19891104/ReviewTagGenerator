#!/bin/bash
pid=$(lsof -i:8082 -t); kill -TERM $pid || kill -KILL $pid
p=$(lsof -i:8108 -t); kill -TERM $p || kill -KILL $p
p3=$(lsof -i:8109 -t); kill -TERM $p3 || kill -KILL $p3
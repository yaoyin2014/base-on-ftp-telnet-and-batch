#!/bin/sh
DetectFlag=$(ps | grep "memtester20" | grep -v "grep" | wc -l)
if [ $DetectFlag -eq 0 ]; then
	echo 1
	exit 1
fi
if [ -f /usr/local/bin/memtest.log ]; then
	echo 1
	exit 1
else
	echo 0
	exit 0
fi

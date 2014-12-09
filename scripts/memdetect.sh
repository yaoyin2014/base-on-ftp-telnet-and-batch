#!/bin/sh
#memtest have been flashed,start to memdetect!
FlashFlag=$(nanddump -p -s 0x48 /dev/mtd0 | grep 0x00000048 | awk -F\: '{print $2}' | awk '{print $1}')
if [ $FlashFlag -eq 38 ]; then
	DetectFlag=$(ps | grep "memtester20" | grep -v "grep" | wc -l)
	if [ $DetectFlag -eq 1 ]; then
		killall memtester20
	fi
	if [ -f /usr/local/bin/memtester ];then
		cp /usr/local/bin/memtester /usr/local/bin/memtester20 
		memtester20 20M &
		echo 0
		exit 0
	else
		echo 1
		exit 1
	fi
else
	echo 1
	exit 1
fi

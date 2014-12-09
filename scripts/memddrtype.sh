#!/bin/sh
FlashFlag=$(nanddump -p -s 0x10 /dev/mtd0 | grep 0x00000010 | awk -F\: '{print $2}' | awk '{print $1}')
if [ $FlashFlag -eq 28 ]; then
	echo 2
	exit 1
else
	echo 3
	exit 0
fi

#!/bin/sh
#start to flash!
FlashFlag=$(nanddump -p -s 0x10 /dev/mtd0 | grep 0x00000010 | awk -F\: '{print $2}' | awk '{print $1}')
if [ $FlashFlag -eq 28 ]; then
	echo 1
	exit 1
fi

ambootMd5=$(cat md5_text | awk '{print $1}')
md5sum amboot_bst_release.bin > sum_text
sumMd5=$(cat sum_text | awk '{print $1}')
if [ $ambootMd5 = $sumMd5 ];then
	touch /usr/local/bin/patch_md_ok
	rm -rf /usr/local/bin/sum_text
	if [ -f /usr/local/bin/amboot_bst_release.bin ];then
		flash_eraseall /dev/mtd0
		nandwrite -p /dev/mtd0  /usr/local/bin/amboot_bst_release.bin
		FlashFlag=$(nanddump -p -s 0x48 /dev/mtd0 | grep 0x00000048 | awk -F\: '{print $2}' | awk '{print $1}')
		if [ $FlashFlag -eq 38 ]; then
			echo 0
			exit 0
		else
			echo 4
			exit 1
		fi
	else
		echo 3
		exit 1
	fi
else
	touch /usr/local/bin/patch_md_fail
	echo 2
	exit 1
fi

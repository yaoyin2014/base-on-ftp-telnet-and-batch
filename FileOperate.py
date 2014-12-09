#coding=utf-8
import os

# 文件路径（含文件名）
def getContent(f,status):
	if os.path.isfile(f):
		f_obj = open(f)
	else:
		return False
	try:
		f_obj.seek(0,0)
		if "whole" == status:
			txts = f_obj.read()
		elif "lines" == status:
			txts = f_obj.readlines()
			txts = [txt.strip() for txt in txts]
	except:
		txts = False
	finally:
		if not f_obj.closed:
			f_obj.close()
	return txts
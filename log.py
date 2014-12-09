# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
#定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
Rthandler = RotatingFileHandler('result.log', maxBytes=10*1024*1024,backupCount=5)
Rthandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(message)s')#'%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)

# logging.warning('192.168.0.1')



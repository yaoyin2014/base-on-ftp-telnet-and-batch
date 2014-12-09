#!/usr/bin/python
#! -*- coding=gbk -*-

import wx
import wx.grid
import wx.lib.dialogs
from ThreadPool import ThreadPool
from TelnetIpc import telnetTask
from Utility import getServerIP

_THREAD_NUMBER = 20

def handler( ips_cmds ):
	
	taskCount = len( ips_cmds )
	if taskCount > _THREAD_NUMBER: 
		threadCount = _THREAD_NUMBER
	else: 
		threadCount = taskCount

	pool=ThreadPool(threadCount)
	for ip, cmds in ips_cmds:
		pool.addTask(telnetTask, ip = ip, cmds = cmds )
	pool.start()

	dlg = wx.ProgressDialog("Waitng", "Waiting",
                          		maximum = taskCount,
                          		parent= None,
                          		#style = wx.PD_CAN_ABORT|wx.PD_APP_MODAL
                      		)
   	while pool.getFinishCount() < taskCount:
   		dlg.Update(pool.getFinishCount(), "%d of %d" %(pool.getFinishCount(), taskCount))         
		wx.MilliSleep(100)	
	dlg.Destroy()
	
	result = pool.show()
	pool.join()#pool itself is also a thread
	return result
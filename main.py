#coding=utf-8
import wx
import os

# 解析IP
from IpParser import IPParser

# 多线程
from ThreadPool import WorkingThread
from ThreadPool import ThreadPool

# telnet
from TelnetIpc import telnetTask

# ftp
from FTPServerProcess import FTPServerProcess

# 公用函数
from Utility import getServerIP
from Utility import alert
from Utility import getCurTime
from Utility import toUnicode

# 多线程执行命令，并显示进度条
from ProgressHandler import handler as _handler

# 日志
import log
import logging

# 子线程通知主线程操作UI
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub

# 文件基本操作
from FileOperate import getContent




_THREAD_POOL_SIZE = 40
_MAIN_WIDTH = 535

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1) 
        
        wx.StaticText(self, -1, "IP:", pos=(10, 20),size=(20,-1))
        self.ip = wx.TextCtrl(self,-1,pos=(30,20),size=(_MAIN_WIDTH-40,-1),value="")

        wx.StaticText(self, -1, "脚本文件名->相机目录".decode("utf-8"), pos=(10, 80),size=(310,-1))
        self.scriptName_cameraPath = wx.TextCtrl(self,-1,pos=(10,110),size=(_MAIN_WIDTH-20,80),style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_READONLY)
        
        imports_file = "./imports/imports.txt"
        
        whole = getContent(imports_file,"whole")
        if False == whole:
            logging.warning((imports_file + "读取失败").decode("utf-8"))
            return
        else:
            self.scriptName_cameraPath.SetValue(whole.decode("utf-8"))
        lines = getContent(imports_file,"lines")
        self.script_name_list = []
        self.camera_path_list = []
        for line in lines:
            self.script_name_list.append((line.split("->")[0]).strip())
            self.camera_path_list.append((line.split("->")[1]).strip())

        self.import_button = wx.Button(self, -1, '导入补丁'.decode("utf-8"), pos=(10, 200), size=(80, 30))
        self.patch_button = wx.Button(self,-1,"修补补丁".decode("utf-8"),pos=(95,200),size=(80,30))
        self.run_detect_button = wx.Button(self,-1,"运行检测程序".decode("utf-8"),pos=(180,200),size=(80,30))
        self.scan_result_button = wx.Button(self,-1,"查看检测结果".decode("utf-8"),pos=(265,200),size=(80,30))
        self.delete_button = wx.Button(self,-1,"删除补丁".decode("utf-8"),pos=(350,200),size=(80,30))
        self.clear_button = wx.Button(self,-1,"清空内容".decode("utf-8"),pos=(435,200),size=(80,30))
        wx.StaticText(self, -1, "结果如下：".decode("utf-8"), pos=(10, 240),size=(100,-1))
        self.result_text = wx.TextCtrl(self, -1,'',pos=(10,270),size=(_MAIN_WIDTH-20, 400), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_READONLY)

        self.Bind(wx.EVT_BUTTON, self.OnImport, self.import_button)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, self.delete_button)

        self.Bind(wx.EVT_BUTTON, self.OnPatch, self.patch_button)
        self.Bind(wx.EVT_BUTTON, self.OnRunDetect, self.run_detect_button)
        self.Bind(wx.EVT_BUTTON, self.OnScanResult, self.scan_result_button)

        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_button)

    def OnClear(self,evt):
        self.result_text.SetValue(("").decode('utf-8'))

    def ParseIp(self,ips):
        parser = IPParser()
        ips_tmp = parser.parse_ip(ips)
        for ip in ips_tmp:
            if False == ip:
                alert(self,"提示","IP无效")
                return False
        return ips_tmp

    def OnDeleteOrImport(self,desc):
        ips = self.ParseIp(self.ip.GetValue().encode('utf-8').split(';'))
        if False == ips:
            return 
        serverIP = getServerIP( ips )#能telnet相机的电脑IP

        cmds = []
        if "OnDelete" == desc:
            desc_success = "所有设备删除补丁成功"
            desc_fail = "以下设备删除补丁失败:\r\n"
            for i in xrange(len(self.script_name_list)):
                cmds.append("cd %s" %(self.camera_path_list[i]))
                cmds.append("rm -rf %s" %(self.script_name_list[i]))
                cmds.append("rm mem*")#删除sh文件自己生成的文件

        elif "OnImport" == desc:
            desc_success = "所有设备导入补丁成功"
            desc_fail = "以下设备导入补丁失败:\r\n"
            for i in xrange(len(self.script_name_list)):
                cmds.append("cd %s" %(self.camera_path_list[i]))
                cmds.append("ftpget -u script -p script %s %s" %(serverIP,self.script_name_list[i]))
                cmds.append("chmod +x %s" %(self.script_name_list[i]))

        cmds = [ cmd.encode("ascii") for cmd in cmds]

        ips_cmds = [ ( ip, cmds) for ip in ips ]


        self.ButtonStatus("Disable")

        # [[ip,[ret1,ret2]],...]
        results = _handler( ips_cmds )


        resultsStr = ""
        ret = ""
        for result in results:
            if ["fail"] == result[1]:
                resultsStr += str(result[0]) + "\r\n"
            
        if "" == resultsStr:
            resultsStr = desc_success
        else:
            resultsStr = desc_fail + resultsStr
        alert(self,"结果",resultsStr)

        resultsStr = self.result_text.GetValue()+getCurTime().decode("ascii")+"    ".decode("utf-8")+resultsStr.decode("utf-8")+"\r\n".decode("utf-8")
        self.result_text.SetValue(resultsStr)
        logging.warning(resultsStr)
        self.ButtonStatus("Enable")

        return ips


    def OnDelete(self, evt):
        self.OnDeleteOrImport("OnDelete")

    def OnImport(self, evt):
        ips = self.OnDeleteOrImport("OnImport")
        
        self.ShowDdrtype(ips)

    def OnPatch(self,evt):

        desc_ddr2 = "DDR2不需要修补补丁\r\n"
        desc_fail = " 修补补丁失败\r\n"
        desc_md5 = "补丁Md5值校验失败\r\n"
        desc_notexist = "补丁文件不存在\r\n"
        desc_success = "所有设备打补丁成功，请断电\r\n"
        cmds_txt = "./cmds/cmds_patch.txt"
        

        ips = self.ParseIp(self.ip.GetValue().encode('utf-8').split(';'))
        if False == ips:
            return
        cmds = getContent(cmds_txt,"lines")
        if False == cmds:
            return
        pool = ThreadPool( _THREAD_POOL_SIZE )
        for ip in ips: 
            pool.addTask( telnetTask, ip = ip, cmds = cmds)

        #必须放在pool.addFinishCb( finish_event,pool=pool)之前
        def finish_event( *args, **kwargs ):
            pool = kwargs['pool']
            result = pool.show()
            # [[ip,[ret1,ret2]],...]
            result_to_show = ""
            for ip_retlist in result:
                ip = ip_retlist[0]
                retlist = ip_retlist[1]
                if ["fail"] == retlist:
                    result_to_show += ip + " Telnet时抛出了异常\r\n"
                else:
                    t = retlist[len(retlist)-1].split("\r\n")
                    status = t[len(t)-2]
                    if "0" == status:
                        pass 
                    elif "1" == status:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                        result_to_show += ip + desc_ddr2
                    elif "2" == status:
                        result_to_show += ip + desc_md5
                    elif "3" == status:
                        result_to_show += ip + desc_notexist
                    elif "4" == status:
                        result_to_show += ip + desc_fail
                    else:
                        result_to_show += ip + "  脚本返回意料之外的值\r\n"
                        last_cmd_result = retlist[len(retlist)-1]
                        logging.warning(toUnicode(last_cmd_result))
                        
            if "" == result_to_show:
                result_to_show = desc_success
                if  "请断电" in desc_success:
                    wx.CallAfter(pub.sendMessage,"importNote",("请将设备断电"))

            logging.warning(result_to_show.decode('utf-8'))
            result_to_show = self.result_text.GetValue()+getCurTime().decode("ascii")+"    ".decode("utf-8")+result_to_show.decode("utf-8")
            self.result_text.SetValue(result_to_show)
            self.ButtonStatus("Enable")

        pool.addFinishCb( finish_event,pool=pool)
        pool.start()

        self.ButtonStatus("Disable")

    def OnRunDetect(self,evt):
        self.OnExecute("run_detect_button")

    def OnScanResult(self,evt):
        self.OnExecute("scan_result_button")

    def GetDdrType(self,ips):
        resultsDict = {"ddr2":[],"ddr3":[],"fail":[]}

        if not ips:
            return resultsDict
        serverIP = getServerIP( ips )#能telnet相机的电脑IP

        cmds = getContent("./cmds/cmds_ddrtype.txt","lines")
        if False == cmds:
            return

        cmds = [ cmd.encode("ascii") for cmd in cmds]

        ips_cmds = [ ( ip, cmds) for ip in ips ]

        # [[ip,[ret1,ret2]],...]
        results = _handler( ips_cmds )

        
        for result in results:
            ip = result[0]
            retlist = result[1]
            if ["fail"] == retlist:
                resultsDict["fail"].append(ip)
            else:
                t = retlist[len(retlist)-1].split("\r\n")
                status = t[len(t)-2]
                if "2" == status:
                    resultsDict["ddr2"].append(ip)
                elif "3" == status:
                    resultsDict["ddr3"].append(ip)
                else:
                    resultsDict["fail"].append(ip)
        
        return resultsDict

    def ShowDdrtype(self,ips):

        self.ButtonStatus("Disable")

        resultsDict = self.GetDdrType(ips)

        # print resultsDict

        ddr2_desc = "********DDR2类型的设备如下(不需要修补补丁)********\r\n"
        ddr3_desc = "********DDR3类型的设备如下********\r\n"
        fail_desc = "********获取DDR类型失败的设备如下********\r\n"
        ddr2_ips = "\r\n".join(resultsDict["ddr2"])
        ddr3_ips = "\r\n".join(resultsDict["ddr3"])
        fail_ips = "\r\n".join(resultsDict["fail"]) 
        _desc = ""
        if ddr2_ips:
            _desc =  _desc+ddr2_desc+ddr2_ips
        if ddr3_ips:
            _desc =  _desc+ddr3_desc+ddr3_ips
        if fail_ips:
            _desc =  _desc+fail_desc+fail_ips

        resultsStr = self.result_text.GetValue()+getCurTime().decode("ascii")+"    ".decode("utf-8")+_desc.decode("utf-8")+"\r\n".decode("utf-8")
        self.result_text.SetValue(resultsStr)
        logging.warning(resultsStr)
        self.ButtonStatus("Enable")
# 以下多线程处理，也可用函数_handler来处理，过程与函数OnDeleteOrImport相同。
# 此处为了测试python的内部函数finish_event是否能访问到外面的变量desc_fail、desc_success，证明能访问到。
# 以及为了使用让子线程通知主线程去更新界面、弹对话框的技术而故意为之。
# 内部函数与javascript的区别之一是：python的函数声明不会提前到顶部
    def OnExecute(self, button_desc):
        if "run_detect_button" == button_desc:
            desc_fail = "运行检查程序返回失败\r\n"
            desc_success = "所有设备运行检查程序返回成功\r\n"
            cmds_txt = "./cmds/cmds_detect.txt"
        
        if "scan_result_button" == button_desc:
            desc_fail = "查看检查结果返回失败\r\n"
            desc_processexit = "设备检测程序异常退出\r\n"
            desc_success = "所有设备查看检查结果返回成功\r\n"
            cmds_txt = "./cmds/cmds_scan.txt"

        ips = self.ParseIp(self.ip.GetValue().encode('utf-8').split(';'))
        if False == ips:
            return
        cmds = getContent(cmds_txt,"lines")
        if False == cmds:
            return
        pool = ThreadPool( _THREAD_POOL_SIZE )
        for ip in ips: 
            pool.addTask( telnetTask, ip = ip, cmds = cmds)

        #必须放在pool.addFinishCb( finish_event,pool=pool)之前
        def finish_event( *args, **kwargs ):
            pool = kwargs['pool']
            result = pool.show()
            # [[ip,[ret1,ret2]],...]
            result_to_show = ""
            for ip_retlist in result:
                ip = ip_retlist[0]
                retlist = ip_retlist[1]
                if ["fail"] == retlist:
                    result_to_show += ip + " Telnet时抛出了异常\r\n"
                else:
                    t = retlist[len(retlist)-1].split("\r\n")
                    status = t[len(t)-2]
                    if "0" == status:
                        pass 
                    elif "1" == status:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                        result_to_show += ip + desc_fail#desc_fail能访问到
                    elif "2" == status:
                        result_to_show += ip + desc_processexit
                    else:
                        result_to_show += ip + "  脚本返回意料之外的值\r\n"
                        last_cmd_result = retlist[len(retlist)-1]
                        logging.warning(toUnicode(last_cmd_result))
                        
            if "" == result_to_show:
                result_to_show = desc_success

            logging.warning(result_to_show.decode('utf-8'))
            result_to_show = self.result_text.GetValue()+getCurTime().decode("ascii")+"    ".decode("utf-8")+result_to_show.decode("utf-8")
            self.result_text.SetValue(result_to_show)
            self.ButtonStatus("Enable")

        pool.addFinishCb( finish_event,pool=pool)
        pool.start()

        self.ButtonStatus("Disable")

    def ButtonStatus(self,status):
        btns = ["self.import_button","self.scan_result_button","self.run_detect_button",
                   "self.patch_button","self.delete_button","self.clear_button"]
        for b in btns:
            exec(b+"."+status+"()")

class MyFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, 
            id, 'DDR3批量工具'.decode("utf-8"), 
            size = (_MAIN_WIDTH, 700),
            style = wx.MINIMIZE_BOX| wx.SYSTEM_MENU| wx.CAPTION| wx.CLOSE_BOX,
            )
        self.panel = panel = MainPanel(self) 

        pub.subscribe(self.Note,"importNote")

    def Note(self,msg):
        data = msg.data
        alert(self,"重要提醒",data)
        
if __name__ == '__main__':
    from processing import freezeSupport
    freezeSupport()

    FTPServer = FTPServerProcess()
    FTPServer.start()

    # app = wx.PySimpleApp(redirect=False)
    app = wx.App(False)
    frame = MyFrame(parent = None, id = -1)
    frame.Show()
    app.MainLoop()

    FTPServer.stop()
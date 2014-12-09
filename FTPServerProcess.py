from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import processing
import wx
import traceback

FTP_PORT = 21

class FrameFail(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size = wx.Size(400,100),)
        text =  "The FTP Server open failed.\r\nPlease check if the port:%d is free or you have the permission" %FTP_PORT
        wx.StaticText(self, -1, text)  

def _ftpserver():    
    try:
        authorizer = DummyAuthorizer()
        authorizer.add_user("script", "script", "scripts/", perm="elradfmw")
        # authorizer.add_user("log", "log", "logs/", perm="elradfmw")
        # authorizer.add_user("result", "result", "results/", perm="elradfmw")
        # authorizer.add_user("fw3", "fw3", "fw3/", perm="elradfmw")

        handler = FTPHandler
        handler.authorizer = authorizer
        server = FTPServer(( "0.0.0.0", FTP_PORT), handler)
        server.serve_forever()
    except:
        app = wx.PySimpleApp()
        traceback.print_exc()
        frame = FrameFail(None)
        frame.Show()
        app.MainLoop()
       

class FTPServerProcess():
    def __init__(self):
        self.p = processing.Process( target = _ftpserver )
       
    def start(self):
        print "Start the FTP Server"
        self.p.start()

    def stop(self):
        print "Stop the FTP Server"
        self.p.terminate()

if __name__ == "__main__":
    _ftpserver()

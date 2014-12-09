#coding=utf-8
import socket
import wx
import time
import chardet
# return one ip of pc，which can connect to one of hosts at port 23
def getServerIP( hosts ):
  serverIP = None
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  for host in hosts:
      try:
          sock.connect( (host, 23) )
      except:
          continue
      serverIP = sock.getsockname()[0]
      return serverIP
  return None

def alert(self,title,data):
  dlg = wx.MessageDialog(self, data.decode("utf-8"),
                             title.decode("utf-8"),
                             wx.OK | wx.ICON_INFORMATION
                             #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                             )
  dlg.ShowModal()
  dlg.Destroy()

def getCurTime():
  return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def toUnicode(s):
  try:
    if isinstance(s,unicode):
      return s
    else:
      encoding = chardet.detect(s)["encoding"]
      return s.decode(encoding)
  except:
    return None#not unicode
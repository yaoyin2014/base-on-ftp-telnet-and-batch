from distutils.core import setup
import py2exe
import glob
import os


setup(windows=["main.py"], 
	options={"py2exe":{"dll_excludes":["MSVCP90.dll"], 
	"bundle_files":1,
	"packages":['wx.lib.pubsub'],
	"includes":[]}},
	)


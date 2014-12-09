#coding=utf-8
import threading
import Queue

class WorkingThread(threading.Thread):
    def __init__(self, workQueue, resultQueue, timeout=1, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.timeout = timeout
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.start()
    
    def run(self):
        while True:
            try:
                callable, args, kwargs = self.workQueue.get( timeout = self.timeout )
            except:
                break
            res = callable(*args, **kwargs)
            self.resultQueue.put( res)

class ThreadPool(threading.Thread):
    def __init__( self, threadCount):
        threading.Thread.__init__(self)
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.threadCount = threadCount
        self.finishCb = None
        self.finishCb_arg = None

    def execute(self):
        self.threads = [ WorkingThread(self.workQueue, self.resultQueue) for i in range(self.threadCount ) ]
        while self.threads:
            thread = self.threads.pop()
            if thread.isAlive():
                thread.join()
    
        if self.finishCb != None:
            self.finishCb( *self.finishCb_arg[0], **self.finishCb_arg[1] ) 

    def getFinishCount(self):
        return self.resultQueue.qsize()

    def run(self):
        self.execute()

    def addTask( self, callable, *args, **kwargs ):
        self.workQueue.put( (callable, args, kwargs) )    

    def addFinishCb(self, callable, *args, **kwargs):
        self.finishCb = callable
        self.finishCb_arg = (args, kwargs)  

    def show(self):
        results = []
        while not self.resultQueue.empty():
            results.append(self.resultQueue.get())
        return results

from multiprocessing import Process, Pipe, current_process
import threading
from multiprocessing.reduction import reduce_connection, rebuild_connection
import os
import pickle

class pipeConnector():
    """
    pipeConnector class to create a connection between two pipe
    connections and run the receiving data as a thread to keep the
    program running in realtime
    """
    parent_conn=""#parent_conn, child_conn = Pipe() 
    data=""
    t1=""
    verbose=False
    keepLooping=True
    def __init__(self): #,parent_conn):
        #self.connectPipe(parent_conn)
        #self.recvPipeData()
        "doNOthing"
    def connectPipe(self,parent_conn):
        """
        set the pipe connection end.  Pretty simple
        """
        self.parent_conn=parent_conn

    def recvPipeData(self):
        """
        run the data receiving as a thread in the background to access data in realtime
        """
        self.t1=threading.Thread(target=self.waitOnData, args=())
        self.t1.start()

    def waitOnData(self):
        """
        The function running as a thread.  This will keep receiving data until keepLooping is set to False
        """
        while self.keepLooping:
            if self.verbose:
                print "waiting on data for parentConn"
            self.data=self.parent_conn.recv()
            if self.verbose:
                print "got data"
        ##self.waitOnData()  ##don't do this as this can lead to recursion depth error.  Use (semi)infinite Loop instead


class pickledPipeConnector():
    """
    pickledPipeConnector works on the same principle as above but will pickle the data before sending it so webservice database applications such as web2py and django can store the string in session data.
    """
    conn=""#parent_conn, child_conn = Pipe() 
    data=" "
    t1=""
    verbose=True
    recvLoop=True
    passKey=""
    connInfo=""

    def __init__(self,connInfo,passKey): #,parent_conn):
        #self.connectPipe(parent_conn)
        #self.recvPipeData()
        #pickled_writer = pickle.dumps(reduce_connection(parent_conn))
        #connInfo=reduce_connection(parent_conn)[1]
        #passKey=current_process().authkey
        #self.pickled_writer=pickled_writer
        self.connInfo=connInfo
        self.passKey=passKey
        #self.session=session
        #self.db=db
        #self.createRow()

    def recvPipeData(self):
        """
        run the data receiving as a thread in the background to access data in realtime
        """
        #self.t1=threading.Thread(target=self.waitOnData, args=())
        #self.t1.start()
        t1=threading.Thread(target=self.waitOnData, args=())
        t1.start()
        print 'started the thread'
        #t1.join()
        #print "thread done"

    def waitOnData(self):
        """
        The function running as a thread.  This will keep receiving data until keepLooping is set to False
        """
        #upw = pickle.loads(self.pickled_writer)
        #writer = upw[0](upw[1][0],upw[1][1],upw[1][2])
        
        while self.recvLoop:
 
            
            if self.verbose:
                print "waiting on data for parentConn"
            self.data=self.conn.recv()
            if self.verbose:
                print "got data"
            #self.waitOnData()


def doSampleStuff(child):
    import time
    x=1
    y=2
    while True:
        x=x+1
        y=y+2
        child.send(['to infinity and beyond',x,y])
        time.sleep(0.1)
    return "done"

def main():
    #script to test pipeConnector
    import pipeHandler
    parent_conn,child_conn=pipeHandler.Pipe()  ##create pipe parent and child
    pH1=pipeHandler.pipeConnector()            ##create pipeConnector
    pH1.connectPipe(parent_conn)               ##used parent conn as the pipe connection for pipeConnector
    pH1.recvPipeData()                         ##start receiving thread
    child_conn.send(['hello parent',3,4,5])    ##send sample data string
    pH1.data ##see the data on the other end 
    ##['hello parent',3,4,5]
    proc1=pipeHandler.Process(target=pipeHandler.doSampleStuff,args=(child_conn,))
    proc1.start()
    pH1.data ##see the data on the other end as the function does it's thing
    #['to infinity and beyond', 11365, 22730]
    #['to infinity and beyond', 11495, 22990]
    #....
    #['to infinity and beyond', 11569, 23138]
    



    ##to test pickled pipe connector between two shells
    # in shell 1
    from pipeHandler import pickledPipeConnector
    from multiprocessing.reduction import reduce_connection
    from multiprocessing import Pipe, current_process
    import pickle

    reader, writer = Pipe()
    pickled_writer = pickle.dumps(reduce_connection(writer))
    passKey=current_process().authkey
    ppC=pickledPipeConnector(pickled_writer,passKey)
    ppC.conn=reader
    ppC.recvPipeData()


    # in shell 2
    from pipeHandler import pickledPipeConnector
    from multiprocessing.reduction import rebuild_connection
    from multiprocessing import Pipe, current_process
    import pickle
    
    #use the passkey and pickled writer from shell 1
    ##here are examples
    passKey='\xe4A-\x18\xd7;&\xdd!5\xa9\xf7\xae\xd5\xd6v\x0c\xb2\x92\x88\x1a\xb3.av\xde\x93s\xd0\x1f!\xf6'
    pickled_writer="(cmultiprocessing.reduction\nrebuild_connection\np0\n((S'/tmp/pymp-_rZWHC/listener-l6qouC'\np1\nI4\nI00\ntp2\nI01\nI01\ntp3\ntp4\n."
    current_process().authkey=passKey   #import passkey
    upw = pickle.loads(pickled_writer)  #import pickled string
    writer = upw[0](upw[1][0],upw[1][1],upw[1][2])
    # writer = rebuild_connection(upw[1][0],upw[1][1],upw[1][2])
    ppC=pickledPipeConnector(pickled_writer,passKey)
    ppC.conn=writer
    ppC.recvPipeData()

    # # now do (almost) any send and recv
    # #in shell 2
    import numpy
    writer.send(['this is data', numpy.arange(10)])


    # #in shell one
    ppC.data  ##should produce the data
    reader.send('hello back')

    # #in shell two
    ppC.data ##should produce the message


# -*- coding:utf-8 -*-
import time
import threading


class PidController(threading.Thread):

    __LAST_UPDATE_TIME=0
    
    #控制频率为50HZ
    RATE = 1 / 50    

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
    
    def run(self):
        self.__LAST_UPDATE_TIME = time.time()        
        while self.isAlive():
            t_start = time.time()
            self.loop()
            t_sleep =self.RATE - (time.time() - t_start)
            if t_sleep > 0:
                time.sleep(t_sleep)
            
    def loop(self):
        a=0


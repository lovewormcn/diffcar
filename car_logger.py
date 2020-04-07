# -*- coding:utf-8 -*-
import time
import threading
from matplotlib import pyplot as plt
import csv


class CarLogger(threading.Thread):
    X = []
    Y = []
    T = []
    ANGEL = []

    __stop = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self):
        while not self.__stop:
            # self.draw_data()
            # self.print_data()
            # self.print_diff()
            time.sleep(0.1)

    def stop(self):
        self.__stop = True

    def stop_and_save(self, file_path):
        self.stop()
        self.save_csv(file_path)

    def log(self, t, x, y, angel):
        self.T.append(t)
        self.X.append(x)
        self.Y.append(y)
        self.ANGEL.append(angel)

    def draw_data(self, plt_id):
        plt.figure(plt_id)
        plt.clf()
        plt.plot(self.X, self.Y)
        plt.draw()
        plt.show()

    def print_data(self):
        if len(self.T) > 0:
            print("%d-%f:[%f,%f,%f]\n" %
                  (len(self.T), self.T[-1], self.X[-1], self.Y[-1], self.ANGEL[-1]))

    def print_diff(self):
        if len(self.T) > 1:
            dt = self.T[-1]-self.T[-2]
            vx = (self.X[-1] - self.X[-2]) / dt
            vy = (self.Y[-1] - self.Y[-2]) / dt
            vangel = (self.ANGEL[-1] - self.ANGEL[-2]) / dt
            print("delta-%f:[%f,%f,%f]\n" %
                  (dt, vx, vy, vangel))

    def save_csv(self, file_path):
        fcsv = open(file_path, 'w+')
        for i in range(0, len(self.T)):
            fcsv.write('%f,%f,%f,%f\n' %
                       (self.T[i], self.X[i], self.Y[i], self.ANGEL[i]))
        fcsv.close()

# -*- coding:utf-8 -*-
import time
import threading
from matplotlib import pyplot as plt
import csv
import math


class CarLogger(threading.Thread):
    X = []
    Y = []
    T = []
    ANGLE = []
    __LENTH_CODER = None

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
        if self.__LENTH_CODER:
            self.save_csv_wheel(file_path)
        else:
            self.save_csv(file_path)

    def log(self, t, x, y, angle):
        self.T.append(t)
        self.X.append(x)
        self.Y.append(y)
        self.ANGLE.append(angle)

    def draw_data(self, plt_id):
        plt.figure(plt_id)
        plt.clf()
        plt.plot(self.X, self.Y)
        plt.draw()
        plt.show()

    def print_data(self):
        if len(self.T) > 0:
            print("%d-%f:[%f,%f,%f]\n" %
                  (len(self.T), self.T[-1], self.X[-1], self.Y[-1], self.ANGLE[-1]))

    def print_diff(self):
        if len(self.T) > 1:
            dt = self.T[-1]-self.T[-2]
            vx = (self.X[-1] - self.X[-2]) / dt
            vy = (self.Y[-1] - self.Y[-2]) / dt
            vangle = (self.ANGLE[-1] - self.ANGLE[-2]) / dt
            print("delta-%f:[%f,%f,%f]\n" %
                  (dt, vx, vy, vangle))

    def save_csv(self, file_path):
        fcsv = open(file_path, 'w+')
        fcsv.write('T,X,Y,ANGLE\n')
        for i in range(0, len(self.T)):
            fcsv.write('%f,%f,%f,%f\n' %
                       (self.T[i], self.X[i], self.Y[i], self.ANGLE[i]))
        fcsv.close()

    def set_lenth_coder(self, LENTH_CODER):
        self.__LENTH_CODER = LENTH_CODER

    def save_csv_wheel(self, file_path):
        fcsv = open(file_path, 'w+')
        fcsv.write('T,X,Y,ANGLE,LX,LY,RX,RY\n')
        for i in range(0, len(self.T)):
            # 轮胎与x轴夹角
            ang_wheel = math.pi / 2 - self.ANGLE[i]
            rx = self.X[i]+self.__LENTH_CODER / 2 * math.cos(ang_wheel)
            ry = self.Y[i]-self.__LENTH_CODER / 2 * math.sin(ang_wheel)
            lx = self.X[i]-self.__LENTH_CODER / 2 * math.cos(ang_wheel)
            ly = self.Y[i]+self.__LENTH_CODER / 2 * math.sin(ang_wheel)
            fcsv.write('%f,%f,%f,%f,%f,%f,%f,%f\n' %
                       (self.T[i], self.X[i], self.Y[i], self.ANGLE[i], lx, ly, rx, ry))
        fcsv.close()

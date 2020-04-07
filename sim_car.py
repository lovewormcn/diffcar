# -*- coding:utf-8 -*-
import math
import threading
import time
from car_logger import CarLogger


class SimCar(threading.Thread):
    x = 0
    y = 0
    angel = 0

    rps_l = 0.0
    rps_r = 0.0
    velocity_l = 0.0
    velocity_r = 0.0

    __logger = None

    # 模拟计算频率200HZ
    __TIME_PER_SPIN = 1 / 100
    # 上一次开始计算的时刻，用于推算距离
    __LAST_SPIN_START_TIME = 0
    # 上一次结束计算的时刻，用于推算距离
    __LAST_SPIN_END_TIME = 0
    # 轮胎半径2cm
    R_WHEEL = 0.02
    # 两轮距离80cm
    LENTH_CODER = 0.8
    # 每个转动角对应的滚动距离
    LENTH_PER_CNT = math.pi * 2 * R_WHEEL / (360 / 0.45)
    # 轮子的转速,1r/s,需要以弧度计算
    RDPS_MAX = 1*2*math.pi
    # 轮子的最大线速度
    VELOCITY_MAX = R_WHEEL * RDPS_MAX

    def __init__(self, x, y, angle, logger):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.x = x
        self.y = y
        self.angel = angle
        self.__logger = logger

    def clone_pose(self):
        return SimCar(self.x, self.y, self.angel, None)

    def distance(self, aCar):
        dx = aCar.x - self.x
        dy = aCar.y-self.y
        return math.sqrt(dx * dx + dy * dy)

    def distance(self, x, y):
        dx = x - self.x
        dy = y-self.y
        return math.sqrt(dx * dx + dy * dy)

    # 模拟一次轮子转到
    def spin_once(self):
        #Dis_L = LENTH_PER_CNT * DeltaCntL
        #Dis_R = LENTH_PER_CNT * DeltaCntR
        # 算出dt,dl,dr,dangel
        dt = time.time()-self.__LAST_SPIN_START_TIME
        Dis_L = self.velocity_l*dt
        Dis_R = self.velocity_r*dt
        Angle_Del = (Dis_R - Dis_L) / self.LENTH_CODER
        # 更新到最新位置
        self.x += (Dis_R+Dis_L)*math.cos(self.angel+Angle_Del)/2
        self.y += (Dis_R+Dis_L)*math.sin(self.angel+Angle_Del)/2
        tmp = self.angel+Angle_Del
        if tmp > math.pi:
            tmp -= 2*math.pi
        elif tmp < -math.pi:
            tmp += 2 * math.pi
        self.angel = tmp

    # 设置左右轮角速度
    def set_rps(self, rps_l, rps_r):
        self.rps_l = rps_l
        self.rps_r = rps_r
        self.velocity_l = self.rps_l * self.R_WHEEL
        self.velocity_r = self.rps_r*self.R_WHEEL
        # 设置左右轮角速度

    def set_velocity(self, velocity_l, velocity_r):
        self.rps_l = velocity_l / self.R_WHEEL
        self.rps_r = velocity_r / self.R_WHEEL
        self.velocity_l = velocity_l
        self.velocity_r = velocity_r

    # 仿真计算
    def run(self):
        self.__LAST_SPIN_START_TIME = time.time()
        while self.isAlive():
            t_spin_start = time.time()
            self.spin_once()
            self.__LAST_SPIN_START_TIME = t_spin_start
            if self.__logger:
                self.__logger.log(t_spin_start,
                                  self.x, self.y, self.angel)

            # 控制计算频率，依据执行耗时，决定睡眠时间
            t_sleep = self.__TIME_PER_SPIN - (time.time()-t_spin_start)
            if t_sleep > 0:
                time.sleep(t_sleep)

    # 坐标转换
    def trans_car_coordinate(self, x, y, angel):
        # 坐标平移
        x = x - self.x
        y = y - self.y
        # 坐标旋转
        roate = -math.pi / 2 + self.angel
        x = x * math.cos(roate) + y * math.sin(roate)
        y = y * math.cos(roate) - x * math.sin(roate)
        angel = angel - roate
        return (x, y, angel)

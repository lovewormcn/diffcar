# -*- coding:utf-8 -*-
import math
from matplotlib import pyplot as plt
import time
from sim_car import SimCar
from car_logger import CarLogger
import os
import sys
import datetime


# 将小车转到目标角度，返回花费的时间
def point_roate(car: SimCar, aim_angel):
    # 计算需要旋转的角度
    dw = aim_angel - car.angel
    if dw > math.pi:
        dw = 2 * math.pi - dw
    elif dw < -math.pi:
        dw = 2 * math.pi + dw
    # 仿真需要花费的时间
    # 设置两轮速度
    wl = -car.RDPS_MAX/10 if dw > 0 else car.RDPS_MAX/10
    wr = -wl
    t = -dw * car.LENTH_CODER / (2 * wl*car.R_WHEEL)
    car.set_rps(wl, wr)
    time.sleep(t)
    car.set_velocity(0, 0)
    print("point roate to %f cost %fs" % (car.angel, t))
    return t


# 将小车向前开指定距离，返回花费的时间
def move_straight(car: SimCar, offset):
    wl = math.copysign(car.VELOCITY_MAX, offset)
    wr = wl
    # 计算指令执行时常
    t = offset / wl
    car.set_velocity(wl, wr)
    time.sleep(t)
    car.set_velocity(0, 0)
    print("move straight to [%f,%f] cost %fs" % (car.x, car.y, t))
    return t


def move_round(car: SimCar, x, y):
    # 将小车从原点沿圆弧移动到x,y位置，返回花费的时间
    #(x, y, _) = car.trans_car_coordinate(x, y, 0)
    # 计算偏航角和左右轮速度比例
    R = abs((x * x + y * y) / (2 * x))
    p = (2 * R - car.LENTH_CODER) / (2 * R + car.LENTH_CODER)
    DW = math.pi-2*abs(math.atan(y/x))
    # 计算左右轮线速度
    if x > 0 and y > 0:
        vl = car.VELOCITY_MAX
        vr = p*vl
    elif x < 0 and y > 0:
        vr = car.VELOCITY_MAX
        vl = p*vr
    elif x < 0 and y < 0:
        vr = -car.VELOCITY_MAX
        vl = p*vr
    else:
        vl = -car.VELOCITY_MAX
        vr = p*vl
    # 计算指令执行时长
    t = (R+car.LENTH_CODER/2)*DW/car.VELOCITY_MAX
    car.set_velocity(vl, vr)
    time.sleep(t)
    car.set_velocity(0, 0)
    print("move round to [%f,%f] cost %fs" % (car.x, car.y, t))
    return t

# 算法一：1.原地调整航向角面向目标点；2.直线行驶；3.原地调整到目标航向角


def plan1(aCar: SimCar, x, y, angel):
    rot = math.atan(y / x)
    d = aCar.distance(x, y)
    t = 0
    if x > 0 and y > 0:
        t += point_roate(aCar, rot)
    elif x < 0 and y > 0:
        t += point_roate(aCar, rot+math.pi)
    elif x < 0 and y < 0:
        t += point_roate(aCar, rot - math.pi)
    else:
        t += point_roate(aCar, rot)
    t += move_straight(aCar, d)
    t += point_roate(aCar, angel)
    print("plan1 time:%f\n" % t)

# 算法二：1.沿弧线移动至目标位置；2.原地调整到目标航向角


def plan2(aCar: SimCar, x, y, angel):
    t = 0
    t += move_round(aCar, x, y)
    t += point_roate(aCar, angel)
    print("plan2 time:%f\n" % t)


if __name__ == '__main__':

    aLogger = CarLogger()
    aLogger.start()
    aCar = SimCar(0, 0, math.pi / 2, aLogger)
    aCar.start()
    aLogger.set_lenth_coder(aCar.LENTH_CODER)
    plan1(aCar, -1, -2, -math.pi/2)
    aLogger.stop_and_save(sys.path[0]+"/car_a_%s.csv" %
                          datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    bLogger = CarLogger()
    bLogger.start()
    bCar = SimCar(0, 0, math.pi / 2, bLogger)
    bCar.start()
    bLogger.set_lenth_coder(bCar.LENTH_CODER)
    plan2(bCar, -1, -2, -math.pi / 2)
    bLogger.stop_and_save(sys.path[0]+"/car_b_%s.csv" %
                          datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

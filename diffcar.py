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
# aim_angle：目标角度，b_sim：是否模拟
def point_roate(car: SimCar, aim_angle, b_sim=True):
    # 计算需要旋转的角度
    dw = aim_angle - car.angle
    if dw > math.pi:
        dw = 2 * math.pi - dw
    elif dw < -math.pi:
        dw = 2 * math.pi + dw
    # 仿真需要花费的时间
    # 设置两轮速度
    wl = -car.RDPS_MAX/10 if dw > 0 else car.RDPS_MAX/10
    wr = -wl
    t = -dw * car.LENTH_CODER / (2 * wl * car.R_WHEEL)
    if b_sim:
        car.set_rps(wl, wr)
        time.sleep(t)
        car.set_velocity(0, 0)
    else:
        car.set_pose(angle=aim_angle)
    print("point roate to %f cost %fs" % (car.angle, t))
    return t


# 将小车向前开指定距离，返回花费的时间
# offset：目标距离，b_sim：是否模拟
def move_straight(car: SimCar, offset, b_sim=True):
    wl = math.copysign(car.VELOCITY_MAX, offset)
    wr = wl
    # 计算指令执行时常
    t = offset / wl
    if b_sim:
        car.set_velocity(wl, wr)
        time.sleep(t)
        car.set_velocity(0, 0)
    else:
        car.set_pose(x=car.x+offset*math.cos(car.angle),
                     y=car.y+offset*math.sin(car.angle))
    print("move straight to [%f,%f] cost %fs" % (car.x, car.y, t))
    return t

# 将小车向前开指定位置，返回花费的时间
# x,y：目标位置，b_sim：是否模拟


def move_round(car: SimCar, x, y, b_sim=True):
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
    if b_sim:
        car.set_velocity(vl, vr)
        time.sleep(t)
        car.set_velocity(0, 0)
    else:
        if x > 0:
            car.set_pose(x=x, y=y, angle=car.angle - DW)
        else:
            car.set_pose(x=x, y=y, angle=car.angle + DW)
    print("move round to [%f,%f] cost %fs" % (car.x, car.y, t))
    return t

# 算法一：1.原地调整航向角面向目标点；2.直线行驶；3.原地调整到目标航向角


def plan1(aCar: SimCar, x, y, angle, b_sim=True):
    rot = math.atan(y / x)
    d = aCar.distance(x, y)
    t = 0
    if x > 0 and y > 0:
        t += point_roate(aCar, rot, b_sim)
    elif x < 0 and y > 0:
        t += point_roate(aCar, rot+math.pi, b_sim)
    elif x < 0 and y < 0:
        t += point_roate(aCar, rot - math.pi, b_sim)
    else:
        t += point_roate(aCar, rot, b_sim)
    t += move_straight(aCar, d, b_sim)
    t += point_roate(aCar, angle, b_sim)
    print("plan1 time:%f\n" % t)
    return t

# 算法二：1.沿弧线移动至目标位置；2.原地调整到目标航向角


def plan2(aCar: SimCar, x, y, angle, b_sim=True):
    t = 0
    t += move_round(aCar, x, y, b_sim)
    t += point_roate(aCar, angle, b_sim)
    print("plan2 time:%f\n" % t)
    return t


if __name__ == '__main__':

    # aLogger = CarLogger()
    # aLogger.start()
    # aCar = SimCar(0, 0, math.pi / 2, aLogger)
    # aCar.start()
    # aLogger.set_lenth_coder(aCar.LENTH_CODER)
    # plan1(aCar, -1, -2, -math.pi/2)
    # aLogger.stop_and_save(sys.path[0]+"/car_a_%s.csv" %
    #                       datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    # bLogger = CarLogger()
    # bLogger.start()
    # bCar = SimCar(0, 0, math.pi / 2, bLogger)
    # bCar.start()
    # bLogger.set_lenth_coder(bCar.LENTH_CODER)
    # plan2(bCar, -1, -2, -math.pi / 2)
    # bLogger.stop_and_save(sys.path[0]+"/car_b_%s.csv" %
    #                       datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    # 只计算花费时间
    file_path = sys.path[0] + \
        "/car_c_%s.csv" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fcsv = open(file_path, 'w+')
    fcsv.write('LENTH_CODER,R_WHEEL,X,Y,ANGLE,T_PLAN1,T_PLAN2,OFFSET\n')
    cCar = SimCar(0, 0, math.pi / 2)
    cCar.configure(0.02, 0.05, math.pi)
    # 圆的半径为1到3，间隔0.1，range必须为整数所以放大了10倍
    for r in range(10, 30, 1):
        # 角度为从0到360，间隔30
        for angle in range(0, 360, 30):
            # 加15度是为了防止在90、180、270度下，plan2出错
            rd = (angle+15)/180*math.pi
            x = r/10 * math.cos(rd)
            y = r/10 * math.sin(rd)
            cCar.set_pose(0, 0, math.pi/2)
            t1 = plan1(cCar, x, y, rd, b_sim=False)
            cCar.set_pose(0, 0, math.pi/2)
            t2 = plan2(cCar, x, y, rd, b_sim=False)
            fcsv.write("%f,%f,%f,%f,%f,%f,%f,%f\n" %
                       (cCar.LENTH_CODER, cCar.R_WHEEL, x, y, angle+15, t1, t2, r/10))
    fcsv.close()

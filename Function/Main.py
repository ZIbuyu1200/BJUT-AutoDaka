import datetime
import threading
import Daka_fun
import logging


def func():
    now_time_begin = datetime.datetime.now()
    Daka_fun.daka_fun()
    now_time_end = datetime.datetime.now()

    timer_over = (now_time_end - now_time_begin).total_seconds()

    print("打卡所用时间 "+str(timer_over)+'s')

    # Time_24h = 86400
    Time_24h = 86400

    print('下一次执行时间 '+str(Time_24h-timer_over)+'s')

    timer = threading.Timer(Time_24h-timer_over, func)

    timer.start()


if __name__ == '__main__':
    # 获取现在时间
    now_time = datetime.datetime.now()
    # 获取明天时间
    next_time = now_time + datetime.timedelta(days=+1)
    next_year = next_time.date().year
    next_month = next_time.date().month
    next_day = next_time.date().day
    # 获取明天自定义的时间
    Time_set = ' 00:01:00'
    next_time = datetime.datetime.strptime(str(
        next_year)+"-"+str(next_month)+"-"+str(next_day)+Time_set, "%Y-%m-%d %H:%M:%S")
    # # 获取昨天时间
    # last_time = now_time + datetime.timedelta(days=-1)

    # 获取距离明天1点时间，单位为秒
    timer_start_time = (next_time - now_time).total_seconds()
    print('Main 开始执行 现在获取距离明天'+Time_set + ' 还有 '+str(timer_start_time)+'s')

    # 定时器,参数为(多少时间后执行，单位为秒，执行的方法)
    # timer = threading.Timer(timer_start_time, func)
    timer = threading.Timer(timer_start_time, func)
    timer.start()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
参考：https://mp.weixin.qq.com/s/U7bWJJiWGdis8zCm_yco1Q
"""

import os
import time
import random
import multiprocessing as mp

def sub_process(name, delay):

    """进程函数"""
    while True:
        time.sleep(delay)
        print('我是子进程%s，进程id为%s'%(name, os.getpid()))

"""
交换数据，队列
队列是进程间交换数据最常用的方式之一，尤其适合生产者——消费者模式。multiprocessing 模块提供了一个和 queue.Queue 近乎一摸一样的 Queue 类，
它的 put () 和 get() 两个方法均默认为阻塞式，这意味着一旦队列为空，则 get() 会被阻塞；一旦队列满，则 put() 会被阻塞。如果使用参数 
block=False 设置读写 put () 和 get() 为非阻塞，则读空或写满时会抛出异常，因此读写队列之前需要使用 enmpy() 或 full() 判断。
Queue 类实例化时可以指定队列长度。
下面的代码，演示了典型的生产者——消费者模式：进程A负责往地上扔钱，进程B负责从地上捡钱
"""

def sub_process_A(q):
    """A进程函数：生产数据"""
    while True:
        time.sleep(5 * random.random())  # 在0-5秒之间随机延时
        q.put(random.randint(10, 100))   # 随机生成[10,100]之间的整数

def sub_process_B(q):
    """B进程函数：使用数据"""

    words = ['哈哈，', '天哪！', '卖狗的！', '咦，天上掉馅饼了？']
    while True:
        print('%s捡到了%d块钱！' % (words[random.randint(0, 3)], q.get()))


"""
管道是除队列之外的另一种进程间通讯的主要方式。multiprocessing 模块提供了 Pipe 类用于管道通讯，默认是双工的，管道的两端都可以 send() 
和 recv()。需要说明的是，recv() 是阻塞式的，并且没有队列那样的 block 参数可以设置是否阻塞。
下面的代码，演示了两个进程猜数字的游戏：进程A在心中默想了一个 [0, 127] 之间的整数，让进程B来猜。如果B猜对了，游戏结束；如果B猜的数字大于
或者小于目标，则A会告诉B大了或者小了，让B继续。
"""

def sub_process_AA(p_end):
    """A进程函数"""

    aim = random.randint(0, 127)
    p_end.send('我在闭区间[0,127]之间想好了一个数字，你猜是几？')
    print('A: 我在闭区间[0,127]之间想好了一个数字，你猜是几？')
    while True:
        guess = p_end.recv()
        time.sleep(0.5 + 0.5*random.random()) # 假装思考一会儿
        if guess == aim:
            p_end.send('恭喜你，猜中了！')
            print('A: 恭喜你，猜中了！')
            break
        elif guess < aim:
            p_end.send('猜小了')
            print('A: 不对，猜小了')
        else:
            p_end.send('猜大了')
            print('A: 不对，猜大了')

def sub_process_BB(p_end):
    """B进程函数"""

    result = p_end.recv()
    n_min, n_max = 0, 127
    while True:
        time.sleep(0.5 + 2*random.random()) # 假装思考一会儿
        guess = n_min + (n_max-n_min)//2
        p_end.send(guess)
        print('B：我猜是%d'%guess)

        result = p_end.recv()
        if result == '恭喜你，猜中了！':
            print('B：哈哈，被我猜中！')
            break
        elif result == '猜小了':
            n_min, n_max = guess+1, n_max
        else:
            n_min, n_max = n_min, guess
    p_end.close()

"""

"""

if __name__ == '__main__':
    print('主进程（%s）开始，按任意键结束本程序' % os.getpid())

    ##
    # p_a = mp.Process(target=sub_process, args=('A', 1))
    # p_a.daemon = False  # 设置子进程为守护进程
    # p_a.start()
    #
    # p_b = mp.Process(target=sub_process, args=('B', 2))
    # p_b.daemon = False  # 如果子进程不是守护进程，主进程结束后子进程可能成为僵尸进程
    # p_b.start()
    #
    # input()

    ## 队列
    # q = mp.Queue(10)
    # p_a = mp.Process(target=sub_process_A, args=(q,))
    # p_a.daemon = True
    # p_a.start()
    #
    # p_b = mp.Process(target=sub_process_B, args=(q,))
    # p_b.daemon = True
    # p_b.start()
    #
    # input()

    ## 管道
    p_end_a, p_end_b = mp.Pipe()
    p_a = mp.Process(target=sub_process_AA, args=(p_end_a, ))
    p_a.daemon = True
    p_a.start()

    p_b = mp.Process(target=sub_process_BB, args=(p_end_b,))
    p_b.daemon = True
    p_b.start()

    p_a.join()
    p_b.join()
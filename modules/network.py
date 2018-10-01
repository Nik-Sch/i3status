# -*- coding: utf-8 -*-
from threading import Thread
import sys
import time
import subprocess
import json
from collections import deque
import re
import colorsys


class Py3status:
    # matebot_text = ''
    fuck_graph = False

    def __humanbytes(self, B):
        B = float(B)
        KB = float(1024)
        MB = float(KB ** 2) # 1,048,576
        GB = float(KB ** 3) # 1,073,741,824
        TB = float(KB ** 4) # 1,099,511,627,776

        if B < KB:
            return '{0:3.0f} By'.format(B)
        elif KB <= B < MB:
            return '{0:3.0f} KB'.format(B/KB)
        elif MB <= B < GB:
            return '{0:3.0f} MB'.format(B/MB)
        elif GB <= B < TB:
            return '{0:3.0f} GB'.format(B/GB)
        elif TB <= B:
            return '{0:3.0f} TB'.format(B/TB)

    def __init__(self):
        thread = Thread(target = self.__watch_thread, args = [])
        thread.start()

    def __watch_thread(self):
        self.network_string = ""
        self.network_color = ''
        amount = 16
        fifo = deque(amount*[1/1024.0], amount)
        process = subprocess.Popen(['ifstat', '-ni', 'enp0s25', '-q', '1'], stdout=subprocess.PIPE)
        global_max = 1/1024.0;
        while process.poll() is None:
            res  = process.stdout.readline()
            regex = re.search('(\d+\.\d+)\s*(\d+\.\d+)', res);
            if regex == None:
                print >> sys.stderr, 'no match' + res
                continue
            rx = regex.group(1)
            tx = regex.group(2)
            s = float(rx) + float(tx)
            if s > global_max:
                global_max = s
            fifo.append(s)
            l = list(fifo)
            avg = sum(l) / amount
            m = max(l)
            res_list = [ int(x / m * 7) for x in l]
            level_str = u'▁▂▃▄▅▆▇█'
            res_list = [ level_str[min(max(x, 0), 7)] for x in res_list]
            res_str = ''.join(res_list)
            if self.fuck_graph:
                res_str = ''
            self.network_string = u'%s max: %s/s cur: %s/s avg: %s/s gmax: %s/s' % (res_str, self.__humanbytes(m*1024), self.__humanbytes(s*1024), self.__humanbytes(avg*1024), self.__humanbytes(global_max*1024))
            color = colorsys.hsv_to_rgb(1, 0, 0.5 + 0.5*m/global_max)
            color8bit = tuple([i*255 for i in color])
            self.network_color = "#%02x%02x%02x" % color8bit

    def click_info(self):
        return {
            'full_text': self.network_string,
            'cached_until': self.py3.time_in(1),
            'color': self.network_color
        }

if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)

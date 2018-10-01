# -*- coding: utf-8 -*-
from threading import Thread
import sys
import time
import subprocess
import json
import re
import os
import colorsys

class Py3status:
    # matebot_text = ''


    def __get_ram(self):
        f = open('/proc/meminfo')
        out = f.read()
        f.close()
        total = re.search('MemTotal:\s*(\d+)', out).group(1);
        free = re.search('MemAvailable:\s*(\d+)', out).group(1);
        percent = 1 - (float(free) / float(total));
        color = colorsys.hsv_to_rgb(0.3 * (1 - percent), 1, 1)
        color8bit = tuple([i*255 for i in color])
        return {
            'full_text': "RAM: %02.0f%%" % (percent*100),
            'cached_until': self.py3.time_in(1),
            'color': "#%02x%02x%02x" % color8bit
        }


    def __get_cpu(self):
        process = subprocess.Popen(['top', '-bn1'], stdout=subprocess.PIPE)
        out, err = process.communicate();
        percent = (100 - float(re.search('%Cpu.*, ([0-9,.]+) id', out).group(1).replace(',', '.'))) / 100
        color = colorsys.hsv_to_rgb(1.0/3.0 * (1 - percent), 1, 1);
        color8bit = tuple([i*255 for i in color])
        return {
            'full_text': "CPU: %02.0f%%" % (percent*100),
            'cached_until': self.py3.time_in(1),
            'color': "#%02x%02x%02x" % color8bit
        }
    def get(self):
        return {
            'cached_until': self.py3.time_in(1),
            'composite': [self.__get_ram(), {'full_text': ', '}, self.__get_cpu()]
        }

if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)

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



    def get_cpu_fan(self):
        process = subprocess.Popen(['sensors'], stdout=subprocess.PIPE)
        out, err = process.communicate();
        regex = re.search('([^\n]*Fan:\s*\d+ RPM)', out);
        if regex == None:
            return {
                'full_text': '',
                'cached_until': self.py3.time_in(1),
                'color': "#FF0000"
            }
        return {
            'full_text': regex.group(1),
            'cached_until': self.py3.time_in(1),
            'color': "#FFFFFF"
        }



    def get_cpu_temp(self):
        returnList = [];

        filename = '/sys/devices/platform/coretemp.0/hwmon/' + os.listdir('/sys/devices/platform/coretemp.0/hwmon')[0]
        for x in range(1,15):
            if os.path.exists(filename + "/temp" + str(x) + "_label"):
                f = open(filename + "/temp" + str(x) + "_label", "r");
                name = f.readline().replace('\n', '');
                f.close();
                f = open(filename + "/temp" + str(x) + "_input", "r");
                value = float(f.readline().replace('\n', ''))/1000;
                f.close();
                f = open(filename + "/temp" + str(x) + "_max", "r");
                maximum = float(f.readline().replace('\n', ''))/1000;
                f.close();
                percent = (value - 20) / (maximum - 20);
                color = colorsys.hsv_to_rgb(1.0/3.0 * (1 - percent), 1, 1);
                color8bit = tuple([i*255 for i in color])
                returnList.append({
                    'full_text': "%s: %.1f°C" % ('Temp', value),
                    'color': "#%02x%02x%02x" % color8bit,
                    'value': value,
                    'cached_until': self.py3.time_in(1),
                })
        returnList.sort(key=lambda x: x['value'], reverse=True)
        return returnList[1];

if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)

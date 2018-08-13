#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script is a simple wrapper which prefixes each i3status line with custom
# information. It is a python reimplementation of:
# http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl
#
# To use it, ensure your ~/.i3status.conf contains this line:
#     output_format = "i3bar"
# in the 'general' section.
# Then, in your ~/.i3/config, use:
#     status_command i3status | ~/i3status/contrib/wrapper.py
# In the 'bar' section.
#
# In its current version it will display the cpu frequency governor, but you
# are free to change it to display whatever you like, see the comment in the
# source code below.
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License (WTFPL), Version
# 2, as published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.

import re
import sys
import json
import subprocess
import codecs
from collections import deque
from threading import Thread
import os
import colorsys
import time
import math

def get_playerctl_color():
    process = subprocess.Popen(['playerctl', 'status'], stdout=subprocess.PIPE)
    playing, err = process.communicate()
    return "#00FF00" if "Play" in playing else "#FFFF00"

def get_playerctl_text():
    process = subprocess.Popen(['playerctl', 'metadata', 'xesam:artist'], stdout=subprocess.PIPE)
    artist, err = process.communicate()
    process = subprocess.Popen(['playerctl', 'metadata', 'xesam:title'], stdout=subprocess.PIPE)
    title, err = process.communicate()
    return '%s - %s' % (artist, title)

def get_uptime():
    process = subprocess.Popen(['uptime', '-p'], stdout=subprocess.PIPE)
    up, err = process.communicate()
    return up[0:-1]

# background thread to provide the string for the network usage
def network_watch_thread():
    global network_string
    network_string = ""
    amount = 32
    fifo = deque(amount*[0], amount)
    while (1):
        process = subprocess.Popen(['ifstat', '-i', 'enp0s25', '-q', '1', '1'], stdout=subprocess.PIPE)
        out, err = process.communicate()
        res = out.splitlines()[-1]
        rx = res.split()[0]
        tx = res.split()[1]
        s = float(rx) + float(tx)
        fifo.append(s)
        l = list(fifo)
        m = max(l)
        res_list = [ int(x / m * 7) for x in l]
        level_str = u'▁▂▃▄▅▆▇█'
        res_list = [ level_str[x] for x in res_list]
        res_str = ''.join(res_list)

        network_string = u'%s, max: %.1f kb/s, cur: %.1f kb/s' % (res_str, m, s)

def get_net():
    return network_string

def get_ram_usage():
    process = subprocess.Popen(['cat', '/proc/meminfo'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    total = re.search('MemTotal:\s*(\d+)', out).group(1);
    free = re.search('MemFree:\s*(\d+)', out).group(1);
    percent = 1 - (float(free) / float(total));
    return "RAM: %02.0f%%" % (percent*100)

def get_ram_color():
    process = subprocess.Popen(['cat', '/proc/meminfo'], stdout=subprocess.PIPE)
    out, err = process.communicate()
    total = re.search('MemTotal:\s*(\d+)', out).group(1)
    free = re.search('MemFree:\s*(\d+)', out).group(1)
    percent = float(free) / float(total)
    color = colorsys.hsv_to_rgb(0.3 * percent, 1, 1)
    color8bit = tuple([i*255 for i in color])
    return "#%02x%02x%02x" % color8bit

def get_cpu_temp():
    returnList = [];
    for x in range(1,15):
        if os.path.exists("/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp" + str(x) + "_label"):
            f  = open("/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp" + str(x) + "_label", "r");
            name = f.readline().replace('\n', '');
            f.close();
            if "Package" not in name:
                continue;
            name = "Core temp"
            f  = open("/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp" + str(x) + "_input", "r");
            value = float(f.readline().replace('\n', ''))/1000;
            f.close();
            f  = open("/sys/devices/platform/coretemp.0/hwmon/hwmon2/temp" + str(x) + "_max", "r");
            maximum = float(f.readline().replace('\n', ''))/1000;
            f.close();
            percent = (value - 20) / (maximum - 20);
            color = colorsys.hsv_to_rgb(1.0/3.0 * (1 - percent), 1, 1);
            color8bit = tuple([i*255 for i in color])
            returnList.append({
                'text': "%s: %.1f°C" % (name, value),
                'color': "#%02x%02x%02x" % color8bit
            })
    return returnList;


def tma_watch_thread():
    global tma
    tma = {'netto': '0:00', 'total': '0:00'}
    global tma_time
    tma_time = 0
    time.sleep(1);
    process = subprocess.Popen(['/home/schelten/.config/i3status/tma_server.js'], stdout=subprocess.PIPE, universal_newlines=True)
    while process.poll() is None:
        tma_string = process.stdout.readline()
        tma = json.loads(tma_string);

        regex = re.search('(\d+):(\d+)', tma['netto']);
        hours = float(regex.group(1));
        minutes = float(regex.group(2));
        tma_time = hours + minutes / 60.0

def get_tma():
    level_str = u' ▁▂▃▄▅▆▇█'
    block = u'█'
    empty = u'░'
    return "%s today: %sh total: %sh" % (''.join([block for i in range(0, int(tma_time))]) + level_str[int(round((tma_time - int(tma_time)) * len(level_str)))] + ''.join([empty for i in range(int(tma_time), 8)]), tma['netto'], tma['total'])

def get_tma_color():
    try:
        percent = min(tma_time, 6.0) / 6.0;
        color = colorsys.hsv_to_rgb(0.3 * percent, 1, 1);
        color8bit = tuple([i*255 for i in color])
        return "#%02x%02x%02x" % color8bit
    except NameError:
        return "";


def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()

if __name__ == '__main__':
    net_thread = Thread(target = network_watch_thread, args = [])
    net_thread.start()

    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())
    tma_thread = Thread(target = tma_watch_thread, args = [])
    tma_thread.start()

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)
        j.insert(-2, {'full_text' : '%s' % get_ram_usage(), 'name' : 'ram', 'color' : get_ram_color()})

        # insert information into the start of the json, but could be anywhere
        j.insert(0, {'full_text' : '%s' % get_playerctl_text(), 'name' : 'playerctl', 'color' : '%s' % get_playerctl_color()})
        j.insert(0, {'full_text' : '%s' % get_net(), 'name' : 'network', 'color' : '#ffffff'})
        j.insert(0, {'full_text' : '%s' % get_tma(), 'name' : 'tma', 'color' : get_tma_color()})
        j.insert(0, {'full_text' : '%s' % get_uptime(), 'name' : 'uptime', 'color' : '#ffffff'})
        x = 0;
        for temp in get_cpu_temp():
            j.insert(0, {'full_text' : '%s' % temp['text'], 'name' : 'cputemp' + str(x), 'color' : temp['color']})
            x += 1

        # and echo back new encoded json
        print_line(prefix+json.dumps(j))

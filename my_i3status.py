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
import gi
import random

gi.require_version('Notify', '0.7')
# from gi.repository import Notify

def humanbytes(B):
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

def get_mate():
    try:
        process = subprocess.Popen(["curl", "-s", "https://anton-schulte.de/matebot/"], stdout=subprocess.PIPE)
        mate, err = process.communicate()
        peoples = json.loads(mate)
        peoples = sorted(peoples, key=lambda x: int(x['konsumiert']), reverse=True)
        rank = 3;
        if (rank > len(peoples)):
            rank = len(peoples);
        leaderboard = {};
        i = 0;
        while (i < rank and len(peoples) > 0):
            dudes = [];
            dudes.append(peoples.pop(0));
            while(len(peoples) > 0 and int(peoples[0]['konsumiert']) == int(dudes[0]['konsumiert'])):
                dudes.append(peoples.pop(0));
            leaderboard[i] = dudes;
            i += len(dudes);
        # print leaderboard
        textArray = [];
        leadershipEmoji = {
        0: u'🥇',
        1: u'🥈',
        2: u'🥉'
        }
        for i in range(rank, -1, -1):
            if i in leadershipEmoji:
                emoji = leadershipEmoji[i]
            else:
                emoji = ''.join([u'💩' for x in range(2, i)])
            if i in leaderboard:
                dudesText = ', '.join(list(map(lambda dude: "%s (%s)" %(dude['name'], dude['konsumiert']), leaderboard[i])));
                textArray.append(emoji + ' ' +  dudesText);
        textArray = textArray[::-1];
        # print ', '.join(textArray)
        return ', '.join(textArray)
    except Exception as e:
        print >> sys.stderr, 'Mate:' + str(e)
        return ''

def get_playerctl():
    process = subprocess.Popen(['playerctl', 'metadata', 'xesam:artist'], stdout=subprocess.PIPE)
    artist, err = process.communicate()
    process = subprocess.Popen(['playerctl', 'metadata', 'xesam:title'], stdout=subprocess.PIPE)
    title, err = process.communicate()
    return '%s - %s' % (artist, title)

def get_playerctl_color():
    process = subprocess.Popen(['playerctl', 'status'], stdout=subprocess.PIPE)
    playing, err = process.communicate()
    return "#00FF00" if "Play" in playing else "#FFFF00"


def get_uptime():
    process = subprocess.Popen(['uptime', '-p'], stdout=subprocess.PIPE)
    up, err = process.communicate()
    return up[0:-1]


def network_watch_thread():
    global network_string
    global network_color
    network_string = ""
    network_color = ''
    amount = 16
    fifo = deque(amount*[1/1024.0], amount)
    process = subprocess.Popen(['ifstat', '-i', 'enp0s25', '-q', '1'], stdout=subprocess.PIPE)
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
        avg = 0
        for entry in l:
            avg += entry
            avg = avg / amount
            m = max(l)
            res_list = [ int(x / m * 7) for x in l]
            level_str = u'▁▂▃▄▅▆▇█'
            res_list = [ level_str[min(max(x, 0), 7)] for x in res_list]
            res_str = ''.join(res_list)
            network_string = u'%s max: %s/s cur: %s/s avg: %s/s gmax: %s/s' % (res_str, humanbytes(m*1024), humanbytes(s*1024), humanbytes(avg*1024), humanbytes(global_max*1024))
            color = colorsys.hsv_to_rgb(1, 0, 0.5 + 0.5*m/global_max)
            color8bit = tuple([i*255 for i in color])
            network_color = "#%02x%02x%02x" % color8bit
def get_net():
    return network_string
def get_net_color():
    return network_color


def get_ram():
    f = open('/proc/meminfo')
    out = f.read()
    f.close()
    total = re.search('MemTotal:\s*(\d+)', out).group(1);
    free = re.search('MemAvailable:\s*(\d+)', out).group(1);
    percent = 1 - (float(free) / float(total));
    return "RAM: %02.0f%%" % (percent*100)

def get_ram_color():
    f = open('/proc/meminfo')
    out = f.read()
    f.close()
    total = re.search('MemTotal:\s*(\d+)', out).group(1)
    free = re.search('MemAvailable:\s*(\d+)', out).group(1)
    percent = float(free) / float(total)
    color = colorsys.hsv_to_rgb(0.3 * percent, 1, 1)
    color8bit = tuple([i*255 for i in color])
    return "#%02x%02x%02x" % color8bit

def get_cpu_fan():
    process = subprocess.Popen(['sensors'], stdout=subprocess.PIPE)
    out, err = process.communicate();
    regex = re.search('([^\n]*Fan:\s*\d+ RPM)', out);
    if regex == None:
        return '';
    return regex.group(1);
def get_cpu_temp():
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
                'text': "%s: %.1f°C" % ('CPU Temp', value),
                'color': "#%02x%02x%02x" % color8bit,
                'value': value
            })
    returnList.sort(key=lambda x: x['value'], reverse=True)
    return returnList[1];

def get_tma():
    try:
        f  = open(os.environ['HOME'] + '/.config/i3status/tma.json', "r");
        tma_string = f.readline();
        f.close();
        tma = json.loads(tma_string);
        if tma['old']:
            # n = Notify.Notification.new("Oh oh", "Logge dich mal lieber wieder ein")
            # n.set_urgency(Notify.Urgency.CRITICAL)
            # n.add_action('asd', 'asd', lambda x: echo(x))
            # os.popen(os.environ['HOME'] + '/.config/i3status/toggle_scratch.js MyTMA -s')
            # n.show()
            return "OH OH";
        regex = re.search('(\d+):(\d+)', tma['netto'])
        netto = int(regex.group(1)) * 60 + int(regex.group(2))
        regex = re.search('(\d+):(\d+)', tma['brutto'])
        brutto = int(regex.group(1)) * 60 + int(regex.group(2))
        level_str = u'░▁▂▃▄▅▆▇█'
        block = u'█'
        empty = u'░'
        progress_bar = ''.join([block for i in range(0, netto/60)]) + level_str[(netto%60)*8/60] + ''.join([empty for i in range(netto/60 + 1, 8)])
        if (brutto - netto) != 0:
            return "%s today: %sh, pause: %smin, total: %sh" % (
            progress_bar,
            tma['netto'],
            (brutto - netto) % 60,
            tma['total'])
        else:
            return "%s today: %sh, total: %sh" % (
            progress_bar,
            tma['netto'],
            tma['total'])
    except Exception as e:
        print >> sys.stderr, 'tma sucks: ' + str(e)
        return ""

def get_tma_color():
    try:
        f  = open(os.environ['HOME'] + '/.config/i3status/tma.json', "r");
        tma_string = f.readline();
        f.close();
        tma = json.loads(tma_string);
        if tma['old']:
            return "#FF0000";
        regex = re.search('(\d+):(\d+)', tma['netto']);
        netto = int(regex.group(1)) * 60 + int(regex.group(2))
        regex = re.search('(\d+):(\d+)', tma['brutto'])
        brutto = int(regex.group(1)) * 60 + int(regex.group(2))
        percent = min(netto, 360.0) / 360.0;
        color = colorsys.hsv_to_rgb(0.3 * percent, 1, 1);
        color8bit = tuple([i*255 for i in color])
        if ((brutto - netto) != 0) and ((brutto - netto) < 30):
            return "#5555ff"
        else:
            return "#%02x%02x%02x" % color8bit
    except Exception:
        return "";
def get_tma_emojis():
    try:
        f  = open(os.environ['HOME'] + '/.config/i3status/tma.json', "r");
        tma_string = f.readline();
        f.close();
        tma = json.loads(tma_string);
        if tma['old']:
            return "OH OH";
        emoji_config = {
            'Kreowsky, Philipp': '🍺',
            'Schelten, Niklas': '🧗',
            'Steinert, Fritjof':'💩',
            'Schulte, Anton': '🏆',
            'Candido, Samuele': '🏃',
            'Stabernack, Benno': '👑',
            'Stec, Michal': '💃',
            'Heine, Carl': 'C',
            'Thieme, Paul': 'P',
            'Vallavanthara, Amal': 'A'
        };
        returnString = '';
        for name, emoji in emoji_config.iteritems():
            for colleague in tma['colleagues']:
                if colleague['name'] == name and colleague['present']:
                    returnString += emoji;
        return '<big>' + returnString + '</big>'
        lastname = re.search('[^/]+$', os.environ['HOME']).group(0).lower();
        colleagues_present = [];
        for colleague in tma['colleagues']:
            if colleague['present'] and re.search('^[^,]*', colleague['name']).group(0).lower() != lastname:
                regex = re.search('^(.).*, (.)', colleague['name'])
                colleagues_present.append(regex.group(2) + regex.group(1))
        return ' '.join(colleagues_present)
    except Exception:
        return "";
def get_cpu_color(text):
    percent = float(re.search('\d+', text).group(0))/100
    color = colorsys.hsv_to_rgb(1.0/3.0 * (1 - percent), 1, 1);
    color8bit = tuple([i*255 for i in color])
    return "#%02x%02x%02x" % color8bit

################################################################################
################################################################################
################################################################################

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

    # Notify.init("Your status bar")

    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        try:
            line, prefix = read_line(), ''
            # ignore comma at start of lines
            if line.startswith(','):
                line = line[1:]
                prefix = ','

            j = json.loads(line)
            for entry in j:
                if entry['name'] == 'cpu_usage':
                    entry['color'] = get_cpu_color(entry['full_text'])
            j.insert(-2, {'full_text' : '%s' % get_ram(), 'name' : 'ram', 'color' : get_ram_color()})

            # insert information into the start of the json, but could be anywhere
            j.insert(0, {'full_text' : '%s' % get_playerctl(), 'name' : 'playerctl', 'color' : '%s' % get_playerctl_color()})
            j.insert(0, {'full_text' : '%s' % get_net(), 'name' : 'network', 'color' : get_net_color()})
            j.insert(0, {'full_text' : '%s' % get_tma(), 'name' : 'tma', 'color' : get_tma_color()})
            j.insert(0, {'full_text' : '%s' % get_uptime(), 'name' : 'uptime', 'color' : '#ffffff'})
            j.insert(0, {'full_text' : '%s' % get_cpu_fan(), 'name' : 'uptime', 'color' : '#ffffff'})
            temp = get_cpu_temp()
            j.insert(0, {'full_text' : '%s' % temp['text'], 'name' : 'cputemp', 'color' : temp['color']})
            j.insert(0, {'full_text' : '%s' % get_tma_emojis(), 'name' : 'tma_emoji', 'color' : '#ffffff', 'markup': 'pango'})
            j.insert(0, {'full_text' : '%s' % get_mate(), 'name' : 'mate', 'color' : '#ffffff', 'markup': 'pango'})


            # and echo back new encoded json
            print_line(prefix+json.dumps(j))
        except Exception as e:
            print >> sys.stderr, 'i3status sucks: ' + str(e)
            print_line("{}");

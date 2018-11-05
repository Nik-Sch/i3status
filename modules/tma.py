# -*- coding: utf-8 -*-
from threading import Thread
import sys
import time
import subprocess
import json
import os
import re
import colorsys
import datetime
class Py3status:
    # matebot_text = ''
    tma_emoji = 'OHOH'
    tma_text = 'OHOH'
    tma_color = '#FF0000'

    def __init__(self):
        thread = Thread(target = self.__watch_thread, args = [])
        thread.start()

    def __watch_thread(self):
        tma = {}
        process = subprocess.Popen([os.environ['HOME'] + '/.config/i3status/tma.js'], stdout=subprocess.PIPE)
        while process.poll() is None:
            tma_string  = process.stdout.readline()
            tma = json.loads(tma_string)
            self.tma_text = self.__get_tma(tma)
            self.tma_color = self.__get_tma_color(tma)
            self.tma_emoji = self.__get_tma_emojis(tma)

    def text(self):
        return {
            'full_text': self.tma_text,
            'cached_until': self.py3.time_in(1),
            'color': self.tma_color
        }

    def emojis(self):
        return {
            'full_text': self.tma_emoji,
            'cached_until': self.py3.time_in(1),
            'markup': 'pango'
        }


    def __get_tma(self, tma):
        try:
            regex = re.search('(\d+):(\d+)', tma['netto'])
            netto = int(regex.group(1)) * 60 + int(regex.group(2))
            regex = re.search('(\d+):(\d+)', tma['brutto'])
            brutto = int(regex.group(1)) * 60 + int(regex.group(2))
            level_str = u'░▁▂▃▄▅▆▇█'
            block = u'█'
            empty = u'░'
            six_hours = (datetime.datetime.now() + datetime.timedelta(0, 60*(360 - netto))).strftime("%H:%M")
            progress_bar = ''.join([block for i in range(0, netto/60)]) + level_str[(netto%60)*8/60] + ''.join([empty for i in range(netto/60 + 1, 8)])
            if (brutto - netto) != 0:
                return u"%s today: %sh, pause: %smin, total: %sh, ⏰ %s" % (
                progress_bar,
                tma['netto'],
                (brutto - netto) % 60,
                tma['total'],
                six_hours)
            else:
                return u"%s today: %sh, total: %sh, ⏰ %s" % (
                progress_bar,
                tma['netto'],
                tma['total'],
                six_hours)
        except Exception as e:
            print >> sys.stderr, 'tma sucks: ' + str(e)
            return ""
    def __get_tma_color(self, tma):
        try:
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
        except Exception as e:
            print >> sys.stderr, 'tma color sucks: ' + str(e)
            return "";

    def __get_tma_emojis(self, tma):
        try:
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
            for colleague in tma['colleagues']:
                found = False
                for name, emoji in emoji_config.iteritems():
                    if colleague['name'] == name and colleague['present']:
                        found = True
                        returnString += emoji;
                if found == False and colleague['present']:
                    regex = re.search('^(.).*, (.)', colleague['name'])
                    returnString += str(regex.group(2))
            return '<big>' + returnString + '</big>'
        except Exception as e:
            print e
            return "";
if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)

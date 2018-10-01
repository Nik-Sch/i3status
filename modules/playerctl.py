# -*- coding: utf-8 -*-
from threading import Thread
import sys
import time
import subprocess
import json

class Py3status:
    # matebot_text = ''

    def get_playerctl(self):
        process = subprocess.Popen(['playerctl', 'metadata', 'xesam:artist'], stdout=subprocess.PIPE)
        artist, err = process.communicate()
        if len(artist) > 0:
            process = subprocess.Popen(['playerctl', 'metadata', 'xesam:title'], stdout=subprocess.PIPE)
            title, err = process.communicate()
            process = subprocess.Popen(['playerctl', 'status'], stdout=subprocess.PIPE)
            playing, err = process.communicate()
            return {
                'full_text': '%s - %s' % (artist, title),
                'cached_until': self.py3.time_in(1),
                'color': "#FF0000" if len(playing) == 0 else "#00FF00" if "Play" in playing else "#FFFF00"
            }
        return {
            'full_text': 'No player running',
            'cached_until': self.py3.time_in(1),
            'color': "#FF0000"
        }
    def on_click(self, event):
        process = subprocess.Popen(['playerctl', 'play-pause'], stdout=subprocess.PIPE)
        playing, err = process.communicate()
if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)

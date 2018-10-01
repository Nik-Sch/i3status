# -*- coding: utf-8 -*-
from threading import Thread
import sys
import time
import subprocess
import json

class Py3status:
    # matebot_text = ''

    def __init__(self):
        matebot_thread = Thread(target = self.__matebot_watch_thread, args = [])
        matebot_thread.start()

    def __matebot_watch_thread(self):
        self.matebot_text = ''
        while True:
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
                self.matebot_text = ', '.join(textArray)
            except Exception as e:
                print >> sys.stderr, 'Mate:' + str(e)
                matebot_text = ''
            time.sleep(1)

    def click_info(self):
        return {
            'full_text': self.matebot_text,
            'cached_until': self.py3.time_in(1)
        }
        
if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)

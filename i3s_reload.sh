#!/bin/bash
cd ~/.config/i3status && if [[ $(git pull | grep -i Already) ]]; then notify-send 'Already up to date'; else i3-msg restart && notify-send 'Updated i3status'; fi

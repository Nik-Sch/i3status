#!/usr/bin/env node

'use strict';

const exec = require("child_process").exec
const commandLineArgs = require('command-line-args')


const {
  env,
  argv
} = require('process');


const args = commandLineArgs([
  {
    name: 'floating',
    alias: 'f',
    type: Boolean
  },
  {
    name: 'forceShow',
    alias: 's',
    type: Boolean
  },
  {
    name: 'title',
    type: String,
    defaultOption: true
  }
]);
console.log(args)
let title = args.title;

function getNodes(data) {
  if (data.output && data.name && data.name.search(title) > -1) {
    console.log('found');
    return data.output.search("__i3") > -1;
  }

  if (data.nodes.length > 0 || data.floating_nodes.length > 0) {
    return data.nodes.concat(data.floating_nodes).reduce((acc, node) => {
      if (acc === true) {
        return true;
      }
      let result = getNodes(node);
      if (result !== null) {
        return result;
      }
      return acc;
    }, null)
  }
  return null;
}


exec("i3-msg -t get_tree", (error, stdout) => {
  j = JSON.parse(stdout);
  let result = getNodes(j)
  if (result == null) {
    if (title.search('calculator')) {
      exec('gnome-calculator &');
    } else if (title.search('MyTMA')) {
      exec("chromium-browser --new-window https://mytma.fe.hhi.de/sinfo/Mytma &");
    } else {
      exec(`notify-send "Couldn't find ${title}. Please open it."`);
    }
  } else if (result) {
    exec(`i3-msg [title=\"${title}\"] move workspace current`);
    if (args.floating) {
      exec(`i3-msg [title=\"${title}\"] floating enable`);
    } else {
      exec(`i3-msg [title=\"${title}\"] floating disable`);
    }

  } else if (args.forceShow !== true) {
    exec(`i3-msg [title=\"${title}\"] move scratchpad`);
  }
});

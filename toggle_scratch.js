#!/usr/bin/env node

const exec = require("child_process").exec
const {
  env,
  argv
} = require('process');

if (argv.length < 3) {
  console.error('Too few arguments. Title is required. Options: -f: make window floating, -s always show');
  return;
} else if (argv.length == 3) {
  argv[3] = ' ';
  argv[4] = ' ';
} else if (argv.length == 4) {
  argv[4] = ' ';
}
let title = argv[2];

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
    if (argv[3].search('f') == -1 && argv[4].search('f') == -1) {
      exec(`i3-msg [title=\"${title}\"] floating disable`);
    } else {
      exec(`i3-msg [title=\"${title}\"] floating enable`);
    }

  } else if (argv[3].search('s') == -1 && argv[4].search('s') == -1) {
    exec(`i3-msg [title=\"${title}\"] move scratchpad`);
  }
});

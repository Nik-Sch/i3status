#!/usr/bin/env node

const exec = require("child_process").exec
const {env, argv} = require('process');

function getNodes(data) {
    if (data.output &&  data.name && data.name.search("MyTMA") > -1) {
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
      exec('notify-send "opened tma"');
      exec("chromium-browser --new-window https://mytma.fe.hhi.de/sinfo/Mytma &");
    } else if (result) {
      exec("i3-msg [title=\"MyTMA\"] move workspace current && i3-msg [title=\"MyTMA\"] floating disable");
    } else if (argv.length < 3) {
        exec("i3-msg [title=\"MyTMA\"] move scratchpad", (err, stdout) => {
          console.error(err, 'err');
          console.error(stdout, 'stdout');
        });
    }
});

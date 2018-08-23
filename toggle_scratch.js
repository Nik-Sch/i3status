#!/usr/bin/env node


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
    name: 'checkClass',
    alias: 'c',
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
  if (data.output && data.name && (args.checkClass ? (data.window_properties && data.window_properties.class.search(title) > -1 ): data.name.search(title) > -1)) {
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
  const checkThing = args.checkClass ? 'class' : 'title';
  const j = JSON.parse(stdout);
  let result = getNodes(j)
  console.log(result, 'result');
  if (result == null) {
    if (title.search('calculator') > -1) {
      exec('gnome-calculator &');
    } else if (title.search('MyTMA') > -1) {
      exec("chromium-browser --new-window --app=https://mytma.fe.hhi.de/sinfo/Mytma &");
    } else {
      exec(`notify-send "Couldn't find ${title}. Please open it."`);
    }
  } else if (result) {
    exec(`i3-msg "[${checkThing}=\"${title}\"] move workspace current"`);
    if (args.floating) {
      exec(`i3-msg "[${checkThing}=\"${title}\"] floating enable"`);
    } else {
      exec(`i3-msg "[${checkThing}=\"${title}\"] floating disable"`);
    }

  } else if (args.forceShow !== true) {
    console.log(`i3-msg "[${checkThing}=\"${title}\"] move scratchpad"`)
    exec(`i3-msg "[${checkThing}=\"${title}\"] move scratchpad"`);
  }
});

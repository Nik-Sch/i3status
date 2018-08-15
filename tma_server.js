#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const {env} = require('process');
let tma = {old: true};
let timeout;
let timeoutHandler = () => {
  tma.old = true;
  fs.writeFileSync(env.HOME + '/.config/i3status/tma.json', JSON.stringify(tma));
}
http.createServer((req, res) => {
  let body = '';
    req.on('data', chunk => {
        body += chunk.toString(); // convert Buffer to string
    });
    req.on('end', () => {
      body = JSON.parse(body);
      Object.keys(body).forEach(key => {
        tma[key] = body[key];
      })
      tma.old = false;
      fs.writeFileSync(env.HOME + '/.config/i3status/tma.json', JSON.stringify(tma));
      clearTimeout(timeout);
      setTimeout(timeoutHandler, 60000);
      res.end('ok');
    });
  res.end();
}).listen(1234);
setTimeout(timeoutHandler, 60000);

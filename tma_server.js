#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const {env} = require('process');
let tma = {};
http.createServer((req, res) => {
  let body = '';
    req.on('data', chunk => {
        body += chunk.toString(); // convert Buffer to string
    });
    req.on('end', () => {
      console.log(body);
        body = JSON.parse(body);
        Object.keys(body).forEach(key => {
          tma[key] = body[key];
        })
        fs.writeFileSync(env.HOME + '/.config/i3status/tma.json', JSON.stringify(tma));
        res.end('ok');
    });
  res.end();
}).listen(1234);

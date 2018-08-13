#!/usr/local/bin/node
const http = require('http');
const fs = require('fs');
http.createServer((req, res) => {
  let body = '';
    req.on('data', chunk => {
        body += chunk.toString(); // convert Buffer to string
    });
    req.on('end', () => {
      console.log(body);
        body = JSON.parse(body);
        fs.writeFileSync('/home/schelten/.config/i3status/tma.json', JSON.stringify(body));
        res.end('ok');
    });
  res.end();
}).listen(1234);

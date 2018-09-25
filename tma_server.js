#!/usr/bin/env node
const request = require('request-promise-native');
const cheerio = require('cheerio');
const fs = require('fs');
const {env} = require('process');
const child_process = require('child_process');

let session = null;
let getTma = async () => {
  var j = request.jar();
  var cookie = request.cookie('JSESSIONID=' + session);
  var url = 'https://mytma.fe.hhi.de';
  j.setCookie(cookie, url);
  let resp = await request({url: 'https://mytma.fe.hhi.de/sinfo/Mytma?formID=START&wahll=ajaxZeitstatus&ajaxFormular=1', jar:j});
  resp = JSON.parse(resp);
  let netto, brutto, total;
  let match = resp.inhalt.match(/(-?\d+:\d+) Std\. \(Nettozeit ohne Pausen\)/i);
  if (match !== null) {
      netto = match[1];
  }

  match = resp.inhalt.match(/(-?\d+:\d+) Std\. \(Bruttozeit inkl. Pausen\)/i);
  if (match !== null) {
      brutto = match[1];
  }

  match = resp.inhalt.match(/heute:<\/td><td[^>]*>(-?\d+:\d+) Std/i);
  if (match !== null) {
      total = match[1];

  }

  resp = await request({
          method: 'POST', 
          url: 'https://mytma.fe.hhi.de/sinfo/Mytma', 
          jar:j,
          form: {
                 formID: 'ANABWES',
		FORMparameter: '',
		listenWahl:     5,
		modulid:        1,
		sprachID: '',
		wahll: 'FormularAuswahl'
          }
  });
$ = cheerio.load(resp);
let colleagues = [];
$('.rundrumZelleMA').each((i, td) => {
	let match = $(td).html().match(/[a-z ]+, [a-z ]+/i);
	if (match !== null) {
		colleagues.push({
		    name: match[0].trim(),
		    present: $(td).attr('title').search('gekommen') > -1
		});
	}
        
});
  tma = {old: false, netto, brutto, total, colleagues};
console.log('updated');
  fs.writeFileSync(env.HOME + '/.config/i3status/tma.json', JSON.stringify(tma));


};
let getSessionId = async () => {
	while(session == null) {
		session = child_process.execSync('zenity --entry --text "Gief Session ID:" --title "SessionID"');
		try{
		var j = request.jar();
		  var cookie = request.cookie('JSESSIONID=' + session);
		  var url = 'https://mytma.fe.hhi.de';
		  j.setCookie(cookie, url);
		let resp = await request({url: 'https://mytma.fe.hhi.de/sinfo/Mytma?formID=START&wahll=ajaxZeitstatus&ajaxFormular=1', jar:j});
	JSON.parse(resp); //Super Hacky aber worked. Wenn falscher Code wird kein JSON zurück gegeben

		} catch(e) {
			console.error(e);
			session = null;
		}
	}
}
(async () => {
	await getSessionId();
	await getTma();
	setInterval(async () => {
		try {
			await getSessionId();
			await getTma();
		} catch(e) {
			session = null;
		}
	}, 10000);
})();

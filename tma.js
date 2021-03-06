#!/usr/bin/env node

const request = require('request-promise-native');
const cheerio = require('cheerio');
const fs = require('fs');
const {
  env
} = require('process');
const child_process = require('child_process');
const FileCookieStore = require('tough-cookie-filestore');
const cookieFile = env.HOME + '/.config/i3status/tma-cookies.json';
if (!fs.existsSync(cookieFile)) {
  fs.writeFileSync(cookieFile, '');
}
let j = request.jar(new FileCookieStore(cookieFile));

let session = null,
  username = null,
  password = null;
const delay = time => new Promise(res => setTimeout(() => res(), time));
let getTma = async () => {
  let resp = await request({
    url: 'https://mytma.fe.hhi.de/sinfo/Mytma?formID=START&wahll=ajaxZeitstatus&ajaxFormular=1',
    jar: j
  });
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
    jar: j,
    form: {
      formID: 'ANABWES',
      FORMparameter: '',
      listenWahl: 5,
      modulid: 1,
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

  resp = await request({
    url: 'https://mytma.fe.hhi.de/sinfo/Mytma',
    jar: j
  });
  let name;
  match = resp.match(/Hallo\s<strong>(\S+).*<\/strong>/i);
  if (match !== null) {
    name = match[1];
  }

  tma = {
    old: false,
    netto,
    brutto,
    total,
    colleagues,
    name
  };
  console.log(JSON.stringify(tma));
  // fs.writeFileSync(env.HOME + '/.config/i3status/tma.json', JSON.stringify(tma));


};
let getLogin = async () => {
  username = child_process.execSync('zenity --entry --text "Gief Username:" --title "tma"').toString().replace('\n', '').trim();
  password = child_process.execSync('zenity --password --text "Gief Password:" --title "tma"').toString().replace('\n', '').trim();
}
let login = async () => {
  await getLogin();
  resp = await request({
    method: 'POST',
    url: 'https://mytma.fe.hhi.de/sinfo/Mytma',
    jar: j,
    form: {
      formID: 'LOGIN',
      user: username,
      datenBank: 0,
      passWord: password,
      wahll: 'FormularAuswahl'
    }
  });
  if (resp.indexOf('Siemens MyTMA - Login') > -1) {
    username = null;
    password = null;
    child_process.execSync(`notify-send 'TMA: Wrong username or password'`);
    await login();
  }
  return true;
  console.log(j);
  console.log(resp);
}
let verifySessionId = async (firstTry = true) => {
  try {
    let resp;
    try {
      resp = await request({
        url: 'https://mytma.fe.hhi.de/sinfo/Mytma?formID=START&wahll=ajaxZeitstatus&ajaxFormular=1',
        jar: j
      });
    } catch (e) {
      //Network error
      if (firstTry) {
        child_process.execSync(`notify-send 'TMA: Could not connect to server'`);
      }
      await delay(1000);
      resp = await verifySessionId(false);
    }
    JSON.parse(resp); //Super Hacky aber worked. Wenn falscher Code wird kein JSON zurück gegeben
  } catch (e) {
    console.error(e);
    await login();
  }
}

if (process.argv.length == 2) {
  (async () => {
    await verifySessionId();
    await getTma();
    setInterval(async () => {
      try {
        await verifySessionId();
        await getTma();
      } catch (e) {
        console.error(e);
      }
    }, 10000);

  })();
} else {
  (async () => {
    await verifySessionId();
    await getTma();
  })()
}

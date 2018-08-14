// ==UserScript==
// @name     Zeiterfassungscript
// @version  1
// @grant    GM.xmlHttpRequest
// @include https://mytma.fe.hhi.de/*
// ==/UserScript==
        let title = document.querySelector('#formularNameDiv').innerText;
console.log(title, 'title');
if (title.search('Startseite') > -1) {

    window.setInterval(() => {

        let netto;
        let total;
        let next = false;
        document.querySelectorAll('#ajaxZeitstatusDiv td').forEach((td, index, all) => {
            let match = td.innerHTML.match(/(\d+:\d+) Std\. \(Nettozeit ohne Pausen\)/i);
            if (match !== null) {
                netto = match[1];
            }

            match = td.innerHTML.match(/heute/i);
            if (match !== null) {
                total = all[index + 1].innerHTML.match(/(\d+:\d+)/)[1];
                console.log(td.innerHTML, all[index + 1].innerHTML);

            }


        });
        GM.xmlHttpRequest({
            method: "POST",
            url: "http://localhost:1234/post.php",
            data: JSON.stringify({netto, total}),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });
    },  2000);
    window.setTimeout(() => {
        window.location.reload();
    }, 10000);
} else if (title.search('Abwesenheit') > -1 ) {
    window.setInterval(() => {

        let colleagues = [];
        let next = false;
        document.querySelectorAll('.rundrumZelleMA').forEach((td, index, all) => {
            console.log(td);
            let match = td.innerHTML.match(/[a-z ]+, [a-z ]+/i);
            if (match !== null) {
                colleagues.push({
                    name: match[0].trim(),
                    present: td.title.search('gekommen') > -1
                });
            }


        });
                        console.log(colleagues);

        GM.xmlHttpRequest({
            method: "POST",
            url: "http://localhost:1234/post.php",
            data: JSON.stringify({colleagues}),
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });
    },  2000);
    window.setTimeout(() => {
        window.location.reload();
    }, 10000);
}

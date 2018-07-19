"use strict";

var ws = new WebSocket("ws://127.0.0.1:9999"),
    log = console.log;

ws.onopen = function () {};

ws.onmessage = function (evt) {};

ws.onclose = function () {};

var enc = function enc(a) {
    var currentdate = new Date();
    var datetime = currentdate.getDate() + "/" + (currentdate.getMonth() + 1) + "/" + currentdate.getFullYear() + "@#" + currentdate.getHours() + ":" + currentdate.getMinutes();
    var x = (datetime + datetime + datetime + datetime).slice(0, 32);
    x = Base64.encode(x);
    var secret = new fernet.Secret(x);
    var token = new fernet.Token({
        secret: secret
    });
    return token.encode("MSG" + JSON.stringify(a));
};

var send = function send(a) {
    var x = enc(a);
    ws.send(x);
};

var sel = function sel(x, y) {
    $("#iserver").val(x);
    $("#iport").val(y);
};

$(document).ready(function () {
    var data = [["GMail", "imap.gmail.com", 993], ["Yandex", "imap.yandex.ru", 993], ["Mail.ru", "imap.mail.ru", 993], ["Rambler", "imap.rambler.ru", 993], ["Outlook", "imap-mail.outlook.com", 993]];
    data.forEach(function (i, a, b) {
        $("#imapsel_dd").append("<li><button type=\"button\" class=\"btn btn-link btn-block\" onclick=\"sel('" + i[1] + "', '" + i[2] + "')\">" + i[0] + "</button></li>");
    });

    $("#save").click(function () {
        var data = {
            imaphost: $("#iserver").val(),
            imapport: $("#iport").val(),
            cred: [$("#email").val(), $("#password").val()],
            snifftime: $("#time").val()
        };
        var ihost_re = new RegExp(/^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/);
        var email_re = new RegExp(/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/);
        var pass_re = new RegExp(/^.{6,}$/g);
        if (ihost_re.test(data.imaphost) && email_re.test(data.cred[0]) && pass_re.test(data.cred[1]) && !isNaN(parseInt(data.imapport)) || !isNaN(parseInt(data.snifftime))) {
            send(data);
            toastr.success("Настройки сохранены на ваш компьютер", "Настройки");
        } else {
            toastr.error("Данные неверно введены", "Настройки");
        }
    });
});
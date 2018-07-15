from utils.StoppableThread import StoppableThread
from utils.websocketserver import WebsocketServer
from werkzeug.utils import secure_filename
from flask import render_template, request
from utils.nocache import nocache
from utils.encryption import *
from flask import Flask
from Main import run
import logging
import json
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'temp')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
enc = EncryptedWay()
mainthread = None
server = None

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def callback(data, cbt=0):
    """
    Callback to send data to front by WS
    :param data: data to send
    :param cbt: type of callback -> 0: append to log, 1: send notify, 2: results modal
    :return:
    """
    res = {'xtype': cbt}
    if type(data) == dict:
        res.update(data)
    else:
        res['data'] = data
    server.send_message_to_all(json.dumps(res, ensure_ascii=False))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@nocache
def index():
    try:
        if request.method == 'POST':
            if 'file' not in request.files:
                raise Exception("No file in request")
            file = request.files['file']
            if file.filename == '':
                raise Exception("File is not a file...")
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                raise Exception("NOT IMPLEMENTED YET")
        else:
            return render_template('index-black.html')
    except Exception as ex:
        return render_template('error.html', res=ex)


@app.route('/settings', methods=['GET', 'POST'])
@nocache
def settings():
    try:
        return render_template('settings-black.html', cred=get_cred())
    except Exception as ex:
        return render_template('error.html', res=ex)


def ws_receive(meta, wss, txt):
    global mainthread
    print("Received by WS:", txt)
    if txt.startswith("NOTENC"):
        data = txt.split(':::')[1:]
        try:
            if data[0] == "START":
                data = json.loads(data[1])
                res = {}
                for name in data['used']:
                    cur = data[name]
                    if type(cur) == list:
                        res[name] = list(map(lambda x: x['norm'] if 'norm' in x else x, cur))
                    else:
                        res[name] = {}
                        for x, y in cur.items():
                            res[name][x] = list(map(lambda j: j['norm'] if 'norm' in j else j, y))
                    if res[name] == {} or res[name] == []:
                        res.pop(name)
                mainthread = StoppableThread(lambda: run(res, callback))
                mainthread.start()
            elif data[0] == "STOP":
                callback({"text": "Сканирование закончено вручную", "title": "Сканирование", "color": "error"}, 1)
                mainthread.stop()
        except Exception as e:
            print(e)
    else:
        data = enc.decrypt(bytes(txt, 'utf-8', ""))
        set_cred(data)


@app.errorhandler(500)
@app.errorhandler(410)
@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(400)
def page_not_found(e):
    return render_template('error.html', res="%d - %s" % (e.code, e.name)), e.code


if __name__ == '__main__':
    server_thread = StoppableThread(lambda: app.run(port=8080, host='0.0.0.0'))
    server_thread.start()

    server = WebsocketServer(9999, host='127.0.0.1', loglevel=logging.INFO)
    server.set_fn_message_received(ws_receive)
    server.run_forever()
    server_thread.stop()

    os.system('kill $PPID')

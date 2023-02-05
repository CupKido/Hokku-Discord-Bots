from flask import Flask, request, abort
import threading
import time

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print(request.json)
    return 'success', 200
    if request.method == 'POST':
        print(request.json)
        return 'success', 200
    else:
        abort(400)


def start_server():
    threading.Thread(target=run_server).start()


def run_server():
    app.run()



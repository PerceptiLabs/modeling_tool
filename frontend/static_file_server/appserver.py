#!/usr/bin/env python

import os, argparse
from flask import Flask, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='../src/dist')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        print('app.static_folder', app.static_folder)
        # print('index.html', index.html)
        return send_from_directory(app.static_folder, 'index.html')

def runServer():
    parser = argparse.ArgumentParser(description='Serves the frontend')
    parser.add_argument('--hostname', 
        help='hostname or ip')
    parser.add_argument('--portnumber', 
        help='port number')
    args = parser.parse_args()

    host = 'localhost' if args.hostname is None else args.hostname
    port = 8080 if args.portnumber is None else args.portnumber

    app.run(host=str(host), port=int(port))

if __name__ == "__main__":
    runServer()
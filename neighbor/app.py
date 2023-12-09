from flask import Flask, jsonify, send_file
import os

VOTES = int(os.getenv('VOTES'))
IMAGE = os.getenv('IMAGE')
TILE = os.getenv('TILE')

app = Flask(__name__)

@app.route('/image')
def GET_image():
    return send_file(IMAGE, mimetype='image/png'), 200

@app.route('/tile')
def GET_tile():
    return send_file(TILE, mimetype='image/png'), 200

@app.route('/votes')
def GET_votes():
    return jsonify({"votes": VOTES}), 200

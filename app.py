import json
from flask import Flask, jsonify, render_template, request
import requests
import dotenv
import os

app = Flask(__name__)

status = 'accept'
xdim = 10
ydim = 10
tilesize = 5
xloc = 0
yloc = 0
voteToken = '45046605-4ef3-4dfc-84ed-cfafade8a2db'

# For simple testing just use one client
approved = 'true'
currentAuthToken = 'none'
currentClientID = 'none'
currentURL = 'none'
currentAuthor = 'none'

UPLOAD_FOLDER = "uploads"

image_requests = []


def init():
    dotenv.load_dotenv()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/getState', methods=['GET'])
def GET_state():
    state = jsonify({
        'status': status,
        'xdim': xdim,
        'ydim': ydim,
        'tilesize': tilesize,
        'xloc': xloc,
        'yloc': yloc,
        'voteToken': voteToken,
        'approved': approved,
        'currentAuthToken': currentAuthToken,
        'currentAuthor': currentAuthor,
        'currentClientID': currentClientID,
        'currentURL': currentURL
    })
    return state, 200


@app.route('/accept', methods=['POST'])
def POST_accept():
    global status
    status = 'accept'
    return "OK", 200


@app.route('/reject', methods=['POST'])
def POST_reject():
    global status
    status = 'reject'
    return "OK", 200


@app.route('/registerImage/<clientID>', methods=["POST"])
def POST_registerImage(clientID):
    if 'file' not in request.files:
        return "", 400

    file = request.files['file']

    if not file or not file.filename or file.filename == '':
        return "", 500

    os.makedirs(UPLOAD_FOLDER + "/" + clientID, exist_ok=True)
    file.save(UPLOAD_FOLDER + "/" + clientID + "/" + file.filename)
    print("file saved")
    return "", 200


@ app.route('/registerClient/<clientID>', methods=["PUT"])
def PUT_registerClient(clientID):
    # this puts a json with the following
    # token : auth token for the server
    # url : "http://server:port/"
    # author : "Your Name"
    data = request.get_json()
    print("registerClient/", clientID, json.dumps(data))

    global currentClientID, currentURL, currentAuthToken, currentAuthor
    currentClientID = clientID
    currentURL = data["url"]
    currentAuthToken = data["token"]
    currentAuthor = data["author"]

    # otherwise return 200 "success" and json with
    # xdim : int // in tiles
    # ydim : int // in tiles
    # tilesize : int
    canvasInfo = jsonify({
        'xdim': xdim,
        'ydim': ydim,
        'tilesize': tilesize
    })

    return canvasInfo, 200


@ app.route("/registeredTest", methods=["GET"])
def GET_registeredTest():

    response = requests.put(f'{currentURL}/registered', json={
        'xloc': xloc,
        'yloc': yloc,
        'voteToken': voteToken,
        'approved': approved,
        'authToken': currentAuthToken,
    })

    return response.text, response.status_code

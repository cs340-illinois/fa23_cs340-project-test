import json
from flask import Flask, jsonify, render_template, request, send_file, Response
import requests
import dotenv
import os

app = Flask(__name__)

status = 'accept'
xdim = 10
ydim = 10
tilesize = 10
xloc = 5
yloc = 5
voteToken = '45046605-4ef3-4dfc-84ed-cfafade8a2db'

# For simple testing just use one client
approved = 'true'
currentAuthToken = 'none'
currentClientID = 'none'
currentURL = 'none'
currentAuthor = 'none'
seq = 0

UPLOAD_FOLDER = "uploads"

image_requests = []
vote_score = {voteToken: 0} # voteToken: score
tile_map = {voteToken: (xloc, yloc)}

def init():
    dotenv.load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

# test GET /image and GET /tile
TILE_SERVER_HOST = 'http://localhost'
TILE_SERVER_PORT = '34000' # change this based on your tile server port

@app.route('/display-image')
def display_image():
    image_response = requests.get(f'{TILE_SERVER_HOST}:{TILE_SERVER_PORT}/image')
    if image_response.status_code == 200:
        return Response(image_response.content, mimetype='image/png')
    else:
        return "Image not available", image_response.status_code

@app.route('/display-tile')
def display_tile():
    tile_response = requests.get(f'{TILE_SERVER_HOST}:{TILE_SERVER_PORT}/tile')
    if tile_response.status_code == 200:
        return Response(tile_response.content, mimetype='image/png')
    else:
        return "Tile not available", tile_response.status_code

# test vote

# You need to add this function to your tile server
# and modify the canvas url to yours

# @app.route('/submit-vote', methods=['POST'])
# def submit_vote():
#     # Extracting xloc and yloc from the request body
#     data = request.get_json()
#     x = data['xloc']
#     y = data['yloc']
    
#     voteToken = token['voteToken']
#     canvas_payload = {
#         "voteToken": voteToken,
#         "xloc": x,
#         "yloc": y
#     }

#     # URL of the canvas server's voting endpoint
#     canvas_url = 'http://127.0.0.1:5000/vote/your_netid'
#     print("start to PUT")
#     # Sending the POST request to the canvas server
#     response = requests.put(canvas_url, json=canvas_payload)
    
#     # Handle the response
#     if response.status_code == 200:
#         print("message", "Vote submitted successfully",200)
#         return jsonify(canvas_payload), 200
#     else:
#         print("error", "Failed to submit vote",response)
#         return jsonify({"error": "Failed to submit vote"}), response.status_code

@app.route('/submit-vote', methods=['POST'])
def proxy_submit_vote():
    data = request.get_json()
    response = requests.post('http://localhost:34000/submit-vote', json=data)
    return jsonify(response.json()), response.status_code

@app.route('/test-GETvotes', methods=['GET'])
def test_vote2():
    url = currentURL + '/votes'
    response = requests.get(url)
    print(jsonify(response.text), response.status_code)
    return jsonify(response.text), response.status_code


@app.route('/test-PUTvotes', methods=['GET'])
def test_vote1():
    response = requests.put(f'{TILE_SERVER_HOST}:{TILE_SERVER_PORT}/votes', json={
        'token': currentAuthToken,
        'votes': vote_score[voteToken],
        'seq': seq,     
    })
    return jsonify(response.text), response.status_code

@app.route('/vote/<clientID>', methods=["PUT"])
def putVotes(clientID):
    data = request.get_json()
    
    # Validating if the necessary data is present
    if not data or 'voteToken' not in data or 'xloc' not in data or 'yloc' not in data:
        return jsonify({"error": "Missing data"}), 400

    # Extracting the voteToken, xloc, and yloc from the request body
    vote_token = data['voteToken']
    dx = data['xloc']
    dy = data['yloc']
    dx = int(dx)
    dy = int(dy)

    if vote_token != voteToken:
        return jsonify({"error": "Invalid vote token"}), 401
    
    # update sequence
    global seq
    seq += 1
    
    # update vote score
    for token in tile_map:
        x, y = tile_map[token]
        if dx == x and dy == y: 
            print("your are voted!")
            vote_score[token] += 1

    print("You vote to tile: ", dx, dy)
    print("Your tile position: ", tile_map[vote_token])
    print("Your vote score: ", vote_score[vote_token])

    return jsonify(data), 200



# Week 1 stuff
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

    print(jsonify(response.text), response.status_code)
    return jsonify(response.text), response.status_code
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

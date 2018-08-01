from hashlib import md5
from flask import Flask, abort, jsonify, redirect, request

app = Flask(__name__)
shortened = {}


def shorten(url):
    return md5(str.encode(url)).hexdigest()

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    if not request.json or 'url' not in request.json:
        print(request.is_json)
        abort(400)
    
    url = request.json['url']
    shortened_url = shorten(url)
    shortened[shortened_url] = url

    return jsonify({'shortened_url': shortened_url}), 201


@app.route('/<alias>', methods=['GET'])
def get_shortened(alias):
    if alias not in shortened:
        abort(400)

    url = shortened[alias]
    if url[:4] != 'http':
        url = 'http://' + url
    return redirect(url, code=302)

if __name__ == '__main__':
    app.run(debug=True)
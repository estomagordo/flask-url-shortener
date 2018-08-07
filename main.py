from base64 import b64encode
from hashlib import blake2b
import random
import re

from flask import Flask, abort, jsonify, redirect, request

app = Flask(__name__)


def url_valid(url):
    """Validates a url by parsing it with a regular expression.

    Parameters:
    url - string representing a url to be validated.

    Return values:
    Boolean, indicating the validity of the url.
    """
    return re.match(regex, url) is not None


def shorten(url):
    """Shortens a url by generating a 9 byte hash, and then
    converting it to a 12 character long base 64 url friendly string.

    Parameters:
    url - the url to be shortened.

    Return values:
    String, the unique shortened url, acting as a key for the entered long url.
    """
    url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    while url_hash in shortened:
        url += str(random.randint(0, 9))
        url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    b64 = b64encode(url_hash.digest(), altchars=b'-_')
    return b64.decode('utf-8')


def bad_request(message):
    """Takes a supplied message and attaches it to a HttpResponse with code 400.

    Parameters:
    message - string containing the error message.

    Return values:
    An object with a message string and a status_code set to 400.
    """
    response = jsonify({'message': message})
    response.status_code = 400
    return response


@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    """POST endpoint that looks for a supplied string called "url",
    contained inside a json object. Then validates this url and
    either returns an error response as appropriate, or generates a
    shortened url, stores the shortened url, and then returns it - if valid.

    Parameters:
    None. However, the global request object should contain the aforementioned json.

    Return values:
    A response signifying success or error.
    Successes contain the shortened url, errors contain an appropriate message.
    """
    if not request.json:
        return bad_request('Url must be provided in json format.')
    
    if 'url' not in request.json:
        return bad_request('Url parameter not found.')
    
    url = request.json['url']
    # For redirection purposes, we want to append http at some point.
    if url[:4] != 'http':
        url = 'http://' + url

    if not url_valid(url):
        return bad_request('Provided url is not valid.')

    shortened_url = shorten(url)
    shortened[shortened_url] = url

    return jsonify({'shortened_url': shortened_url}), 201


@app.route('/shorten_url', methods=['GET'])
def shorten_url_get():
    """GET endpoint that provides a more useful error message for when
    a user of the api tries to shorten a url through GET.

    Parameters:
    None.

    Return values:
    A response with an appropriate error message and a 400 code.
    """
    return bad_request('Must use POST.')


@app.route('/<alias>', methods=['GET'])
def get_shortened(alias):
    """GET endpoint that takes an alias (shortened url) and redirects if successfull.
    Otherwise returns a bad request.

    Arguments:
    alias, the string representing a shortened url.

    Return values:
    A Flask redirect, with code 302.
    """
    if alias not in shortened:
        return bad_request('Unknown alias.')

    url = shortened[alias]
    
    return redirect(url, code=302)

# From https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not#7160778
# Slightly modified to not use ftp.
regex = re.compile(
        r'^(?:http)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
DIGEST_SIZE = 9  # 72 bits of entropy.
shortened = {}

if __name__ == '__main__':
    app.run(debug=True)
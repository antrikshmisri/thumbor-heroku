import os
from hmac import new as new_digester
from hashlib import sha1
from base64 import urlsafe_b64encode

from flask import Flask, jsonify, request

app = Flask(__name__)


def generate_signature(key, unsafe_url):
  """Generate a signature from the given key.
  
  Parameters
  ----------
  key: str
    The key to use for the signature

  Returns
  -------
  str
    The signature string
  """
  unsafe_url = bytes(unsafe_url, 'utf-8')
  key = bytes(key, 'utf-8')

  digester = new_digester(key, unsafe_url, sha1)
  signature = digester.digest()

  safe_signature = urlsafe_b64encode(signature)
  return str(safe_signature, 'utf-8')


def generate_safe_url(key, width, height, image_url):
  """Generate a safe url from the given parameters.
  
  Parameters
  ----------
  width: int
    The width of the image

  height: int
    The height of the image

  image_url: str
    The url of the image

  Returns
  -------
  str
    The safe url
  """
  unsafe_url = f"{width}x{height}/{image_url}"
  signature = generate_signature(key, unsafe_url)
  safe_url = f"/{signature}/{unsafe_url}"
  return safe_url


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello World'}), 200


@app.route('/encode', methods=['GET'])
def encode():
  key = os.getenv('KEY', "1234567890")
  query_params = request.args.to_dict()

  width = query_params.get('width')
  height = query_params.get('height')
  image_url = query_params.get('image_url')

  if not all([width, height, image_url]):
    return jsonify({'error': 'Missing required parameters'}), 400

  try:
    width = int(width)
    height = int(height)
  except ValueError:
    return jsonify({'error': 'Invalid width or height'}), 400

  safe_url = generate_safe_url(key, width, height, image_url)

  _host_name = request.url_root.split(":")
  _host_name.pop()
  _host_name = ":".join(_host_name)

  _server_url = f"{_host_name}:{os.getenv('THUMBOR_PORT', 8080)}"
  safe_url = _server_url + safe_url

  return jsonify({'url': safe_url}), 200

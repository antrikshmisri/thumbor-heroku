import os
from subprocess import PIPE, Popen

from flask import Flask, jsonify, request

app = Flask(__name__)


def run_command(command):
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()

    _return_dict = {
        "out": out,
        "err": err,
        "returncode": p.returncode
    }

    return _return_dict


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello World'}), 200


@app.route('/encode', methods=['GET'])
def encode():
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

  _command = f"thumbor-url --key='1234567890' --width={width} --height={height} {image_url}"
  _output = run_command(_command)

  if _output["err"]:
    return jsonify({'error': 'Something went wrong'}), 500

  _replace_sequence = [
      "\r\n",
      "URL:"
  ]

  _output["out"] = _output["out"].decode('utf-8')

  for _replace in _replace_sequence:
    _output["out"] = _output["out"].replace(_replace, "")

  _host_name = request.url_root.split(":")
  _host_name.pop()
  _host_name = ":".join(_host_name)
  
  _server_url = f"{_host_name}:{os.getenv('THUMBOR_PORT', 8080)}"
  _output["out"] = _server_url + _output["out"]

  return jsonify({'url': _output["out"]}), 200

#!/usr/bin/python3
import re
import sys
import json
import os
from flask import Flask, jsonify, request, abort
from subprocess import call

app = Flask(__name__)

info_json = {
    'Author': u'Yancy Ribbens',
    'description': u'REST API for cert-issuer',
    'version': u'Pilot'
    }

@app.route('/cert_issuer/api/v1.0/issue_cert', methods=['POST'])
def create_cert():
    if not request.json or not 'id' in request.json:
        abort(400)
    file_name = request.json['id'] + '.json' 
    full_path_name = '/etc/cert-issuer/data/unsigned_certificates/' + file_name
    with open(full_path_name, 'w') as outfile:
        json.dump(request.json, outfile)
    call('cert-issuer')
    os.remove(full_path_name)
    with open('/etc/cert-issuer/data/blockchain_certificates/' + file_name) as data_file:
        blockchain_cert = json.load(data_file)
    return jsonify(blockchain_cert), 201

@app.route('/cert_issuer/api/v1.0/certs/<string:cert_id>', methods=['GET'])
def get_blockchain_cert(cert_id):
    with open('/etc/cert-issuer/data/blockchain_certificates/' + cert_id + '.json') as data_file:
        blockchain_cert = json.load(data_file)
    return json.dumps(blockchain_cert)

@app.route('/cert_issuer/api/v1.0/info', methods=['GET'])
def info():
    return jsonify({'info': info_json})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

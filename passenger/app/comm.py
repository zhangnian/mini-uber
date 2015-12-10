# -*- coding: utf-8 -*-

from flask import make_response, jsonify


def make_json(code, msg, data = None):
    if not data:
        data = {}

    dict_args = {"code":code, 'msg':msg, 'data':data}
    resp = make_response(jsonify(dict_args))
    return resp, 200


def make_succ(data = None):
    return make_json(0, "success", data)


def make_err(code, msg):
    return make_json(code, msg)
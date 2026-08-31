"""Consistent API response envelopes, per master prompt §36."""
from flask import jsonify


def success(data=None, status_code: int = 200, **extra):
    body = {"success": True, "data": data if data is not None else {}}
    body.update(extra)
    return jsonify(body), status_code


def error(code: str, message: str, status_code: int = 400):
    return jsonify({"success": False, "error": {"code": code, "message": message}}), status_code

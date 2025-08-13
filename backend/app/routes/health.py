from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    return jsonify({"ok": True, "service": "hotel-app", "version": 1})

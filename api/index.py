import traceback
from flask import Flask, jsonify

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core import app
except Exception as e:
    app = Flask(__name__)
    crash_traceback = traceback.format_exc()
    import logging
    logging.error("Startup crash: " + crash_traceback)

    @app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def catch_all(path):
        return jsonify({"error": "Vercel Boot Error", "traceback": crash_traceback}), 500

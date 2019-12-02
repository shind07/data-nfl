from flask import (
    abort,
    Flask,
    g,
    jsonify,
    request
)
from importlib import import_module
import logging
import os
import sys

import db
import config

sys.path.insert(0, config.API_DIR)
logging.basicConfig(level=logging.INFO, format='{%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
app = Flask(__name__)


def get_db():
    """Get global connection to the db."""
    if 'db' not in g:
        g.db = db.connect_to_db()
    return g.db


@app.route("/")
def hello_world():
    logging.info("calling hello world..")
    return jsonify("hello world!")


@app.route("/api/<path:path>", methods=['GET'])
def api_handler(path):
    """Routes the request to the proper controller (*.py module in api/) and
    entrypoint (function to call within that module).

    :param controller_name: path of controller/entrypoint
    :type controller_name: str (containing '/'s)
    """
    path = path.split("/")
    if len(path) == 0 or len(path) > 2:
        logging.info(f"Invalid path received: {path}")
        abort(404)

    valid_controllers = [f[:-3] for f in os.listdir(config.API_DIR) if f.endswith(".py")]
    controller_name = path[0]
    if controller_name not in valid_controllers:
        logging.info(f"Invalid attempt to access controller {controller_name}.")
        abort(404)
    controller = import_module(controller_name, config.API_DIR)

    valid_entrypoints = [e for e in dir(controller) if not e.startswith("__") and not e.endswith("__")]
    entrypoint_name = "main" if len(path) == 1 else path[1]
    if entrypoint_name not in valid_entrypoints:
        logging.info(f"Invalid attempt to access entrypoint {entrypoint_name} for controller {controller_name}.")
        abort(404)
    entrypoint = getattr(controller, entrypoint_name)

    db_conn = get_db()
    kwargs = {k: v for k, v in request.args.lists()}
    return entrypoint(db_conn, **kwargs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

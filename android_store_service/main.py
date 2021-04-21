# Copyright 2019 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import time

import flask

import shumway
from flask import request, g
from googleapiclient.errors import HttpError
from werkzeug.exceptions import NotFound
from flask_cors import CORS

from android_store_service import exceptions
from android_store_service.resources.apks_resources import apks_blueprint
from android_store_service.resources.builds_resources import builds_blueprint
from android_store_service.exceptions import BadRequestException
from android_store_service.utils import logging_utils
from android_store_service.resources.bundles_resources import bundles_blueprint
from android_store_service.resources.tracks_resources import tracks_blueprint

GIGA_UNIT = 1e9

app = flask.Flask(__name__)
CORS(app)

try:
    app.config.from_envvar("APP_CONFIG_FILE")
except RuntimeError:
    app.config.from_object("config.default_config")

app.register_blueprint(builds_blueprint, url_prefix="/v1")
app.register_blueprint(tracks_blueprint, url_prefix="/v1")
app.register_blueprint(bundles_blueprint, url_prefix="/v1")
app.register_blueprint(apks_blueprint, url_prefix="/v1")


def _check_run_test():
    if os.environ.get("RUNTEST"):
        app.config["LOCAL"] = True
    else:
        pass


def _setup_metrics():
    return shumway.MetricRelay(
        app.config.get("METRICS_KEY"), app.config.get("METRICS_FFWD_HOST")
    )


_check_run_test()
logging_utils.setup_logging(app.config)
metrics = _setup_metrics()
request_times = {}


def ffwd_metric(metric, value, attrs={}):
    attrs["project"] = "some_project"
    metrics.emit(metric, value, attributes=attrs)


@app.before_request
def start_request_timer():
    request_times[hash(flask.request)] = time.perf_counter()


@app.before_request
def send_metrics_received_request():
    ffwd_metric("incoming-request", time.perf_counter())


@app.before_request
def set_request_id():
    g.request_id = logging_utils.get_request_id()


@app.after_request
def send_request_metric(response):
    attrs = {
        "endpoint": flask.request.endpoint,
        "method": flask.request.method,
        "status_code": response.status_code,
    }
    start_time = request_times.pop(hash(flask.request), None)
    if start_time is not None:
        resp_time = time.perf_counter() - start_time
        ffwd_metric("request-time", resp_time * GIGA_UNIT, attrs)
    return response


@app.after_request
def add_request_id_to_response(response):
    response.headers["X-Request-Id"] = g.request_id
    return response


@app.errorhandler(Exception)
def handle_error(error):
    logging.exception(error)
    response = flask.jsonify({"error": {"message": str(error)}})
    response.status_code = 500

    ffwd_metric("500-request", time.perf_counter())
    return response


@app.errorhandler(NotFound)
def handle_not_found_exception(error):
    logging.exception(error)
    response = flask.jsonify({"error": {"message": str(error)}})
    response.status_code = 404
    return response


@app.errorhandler(BadRequestException)
def handle_bad_request(error):
    logging.exception(error)
    response = flask.jsonify({"error": {"message": str(error)}})
    response.status_code = 400

    ffwd_metric("400-request", time.perf_counter())
    return response


@app.errorhandler(HttpError)
def google_api_client_exception(httperror):
    logging.exception(httperror)
    error = exceptions.parse_httperror(httperror)
    response = flask.jsonify(error)
    response.status_code = httperror.resp.status
    return response


@app.before_request
def log_request():
    data = (f" DATA: {request.get_data()}" if request.get_data() else "")[:1000]
    logging.info(
        "%s /%s%s", request.method, request.url.replace(request.url_root, ""), data
    )


@app.route("/status")
def status():
    logging.info("Status: ok")
    response = flask.jsonify({"status": "ok"})
    response.status_code = 200
    return response


def main():
    app.run(debug="debug")  # pragma: no cover


# Run app
if __name__ == "__main__":  # pragma: no cover
    main()

# -*- coding: utf-8 -*-
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
import sys
import flask

from pythonjsonlogger import jsonlogger


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return record


def get_request_id():
    if flask.has_request_context():
        return flask.request.headers.get("X-Request-Id", "")
    return ""


def setup_logging(app_config):
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(
                log_record, record, message_dict
            )
            log_record["severity"] = log_record["levelname"]
            log_record["service_name"] = "android-store-service"
            del log_record["levelname"]

    root_logger = logging.getLogger("")
    root_logger.setLevel(app_config.get("LOGGING_LEVEL"))
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(
        CustomJsonFormatter(
            "%(asctime)s %(levelname)s \
             %(request_id)s %(service_name)s \
             %(message)s",
            "%Y-%m-%dT%H:%M:%S",
        )
    )

    root_logger.handlers = []
    root_logger.addHandler(handler)
    return root_logger

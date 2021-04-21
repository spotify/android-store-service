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
import json
from unittest.mock import patch

from googleapiclient.errors import HttpError
import pytest

from android_store_service import main
from android_store_service.exceptions import NotFoundException, BadRequestException
from tests.helpers.mock_utils import MockGooglePlayResponse, mock_httperror_content


@pytest.fixture
def test_client():
    return main.app.test_client()


basic_route_params = [("/status", 200, {"status": "ok"})]


@pytest.mark.parametrize("route,exp_code,exp_rsp_data", basic_route_params)
def test_basic_routes(test_client, route, exp_code, exp_rsp_data):
    rsp = test_client.get(route)

    assert rsp.status_code == exp_code
    assert json.loads(rsp.data) == exp_rsp_data


negative_route_params = [
    (
        "/nothingheeere",
        "",
        404,
        {
            "error": {
                "message": "404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
            }
        },
    ),
    ("/status", BadRequestException("message"), 400, {"error": {"message": "message"}}),
    (
        "/status",
        NotFoundException("message"),
        404,
        {"error": {"message": "404 Not Found: message"}},
    ),
    ("/status", Exception("message"), 500, {"error": {"message": "message"}}),
    (
        "/status",
        HttpError(
            MockGooglePlayResponse(403),
            json.dumps(mock_httperror_content(403, "error_msg")).encode("utf-8"),
        ),
        403,
        {"error": {"code": 403, "message": "error_msg"}},
    ),
    (
        "/status",
        HttpError(
            MockGooglePlayResponse(403), json.dumps({"foo": "bar"}).encode("utf-8")
        ),
        403,
        {"foo": "bar"},
    ),
    (
        "/status",
        HttpError(
            MockGooglePlayResponse(403), "Error is not JSON format".encode("utf-8")
        ),
        403,
        {"error": {"message": "Error is not JSON format"}},
    ),
    (
        "/status",
        HttpError(MockGooglePlayResponse(403), "".encode("utf-8")),
        403,
        {"error": {"message": ""}},
    ),
]


@patch("logging.info")
@pytest.mark.parametrize("route,exception,exp_code,exp_rsp_data", negative_route_params)
def test_negative_routes(
    mock_logging, test_client, route, exception, exp_code, exp_rsp_data
):
    mock_logging.side_effect = [exception]
    rsp = test_client.get(route)

    assert rsp.status_code == exp_code
    assert rsp.json == exp_rsp_data

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

import httplib2
import pytest
from googleapiclient.errors import HttpError

from android_store_service import main


@pytest.fixture
def test_client():
    return main.app.test_client()


basic_route_params = [
    (
        "/v1/com.package.name/bundles",
        {
            "tracks": ["alpha"],
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        (
            "com.package.name",
            ["alpha"],
            [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
            False,
        ),
    ),
    (
        "/v1/com.package.name/bundles",
        {
            "tracks": ["alpha"],
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
            "dry_run": True,
        },
        (
            "com.package.name",
            ["alpha"],
            [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
            True,
        ),
    ),
    (
        "/v1/com.package.name/bundles",
        {
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
            "dry_run": False,
        },
        (
            "com.package.name",
            [],
            [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
            False,
        ),
    ),
]


@patch("android_store_service.resources.bundles_resources.bundles_logic")
@pytest.mark.parametrize("route,payload,exp_params", basic_route_params)
def test_bundles_resources(bundles_logic_mock, test_client, route, payload, exp_params):
    bundles_logic_mock.upload_bundles.return_value = [123, 123, 123]
    response = test_client.post(route, data=json.dumps(payload))
    bundles_logic_mock.upload_bundles.assert_called_once_with(*exp_params)
    assert response.status_code == 200


negative_route_params = [
    ("/v1/com.package.name/bundles", {}, 400, "'bundles' is a required property"),
    (
        "/v1/com.package.name/bundles",
        {"bundles": []},
        400,
        "Failed validating 'minItems' in schema['properties']['bundles']",
    ),
    ("/v1/com.package.!%/bundles", {}, 400, "Invalid package name"),
]


@patch("android_store_service.resources.bundles_resources.bundles_logic")
@pytest.mark.parametrize(
    "route,payload,exp_response_code,exp_response_message", negative_route_params
)
def test_negative_bundles_resources(
    bundles_logic_mock,
    test_client,
    route,
    payload,
    exp_response_code,
    exp_response_message,
):
    response = test_client.post(route, data=json.dumps(payload))
    assert response.status_code == exp_response_code
    data = json.loads(response.data)
    assert exp_response_message in data["error"]["message"]
    bundles_logic_mock.upload_bundles.assert_not_called()


logic_negative_route_params = [
    (
        "/v1/invalid.package/bundles",
        {
            "tracks": ["alpha"],
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "greatest bundle",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        Exception("Exception"),
        500,
        "Exception",
    ),
    (
        "/v1/invalid.package/bundles",
        {
            "tracks": ["alpha"],
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "greatest bundle",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        HttpError(
            httplib2.Response({"status": 400}),
            content='{"error":{"message": "invalid.package does not exist"}}'.encode(),
        ),
        400,
        "invalid.package does not exist",
    ),
]


@patch("android_store_service.resources.bundles_resources.bundles_logic")
@pytest.mark.parametrize(
    "route,payload,exp_logic_response,exp_response_code,exp_response_message",
    logic_negative_route_params,
)
def test_logic_negative_response(
    bundles_logic_mock,
    test_client,
    route,
    payload,
    exp_logic_response,
    exp_response_code,
    exp_response_message,
):
    bundles_logic_mock.upload_bundles.side_effect = [exp_logic_response]
    response = test_client.post(route, data=json.dumps(payload))
    assert response.status_code == exp_response_code
    assert exp_response_message in json.loads(response.data)["error"]["message"]

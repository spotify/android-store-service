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


post_builds_bundles_params = [
    (
        "/v1/com.package.name/builds",
        {
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                },
                {
                    "sha1": "456",
                    "sha256": "91210",
                    "media_body": "greatestbundle",
                    "deobfuscation_file": "1248765kjbskdf",
                },
            ]
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
                },
                {
                    "sha1": "456",
                    "sha256": "91210",
                    "media_body": "greatestbundle",
                    "deobfuscation_file": "1248765kjbskdf",
                },
            ],
            False,
        ),
    ),
    (
        "/v1/com.package.name/builds",
        {
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                },
                {
                    "sha1": "456",
                    "sha256": "91210",
                    "media_body": "greatestbundle",
                    "deobfuscation_file": "",
                },
            ],
            "tracks": ["alpha", "beta"],
            "dry_run": True,
        },
        (
            "com.package.name",
            ["alpha", "beta"],
            [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "ur673462y",
                    "deobfuscation_file": "1248765kjbskdf",
                },
                {
                    "sha1": "456",
                    "sha256": "91210",
                    "media_body": "greatestbundle",
                    "deobfuscation_file": "",
                },
            ],
            True,
        ),
    ),
]


@patch("android_store_service.resources.builds_resources.apks_logic")
@patch("android_store_service.resources.builds_resources.bundles_logic")
@pytest.mark.parametrize("route,payload,exp_params", post_builds_bundles_params)
def test_build_upload_bundle_resources(
    bundles_logic, apks_logic, test_client, route, payload, exp_params
):
    bundles_logic.upload_bundles.return_value = [123, 123, 123]
    response = test_client.post(route, data=json.dumps(payload))
    bundles_logic.upload_bundles.assert_called_once_with(*exp_params)
    assert response.status_code == 200
    apks_logic.upload_apks.assert_not_called()


negative_route_params = [
    ("/v1/com.package.name/builds", {}, 400, "No payload"),
    ("/v1/com.package.name/builds", {"tracks": ["alpha"]}, 400, "No binaries"),
    ("/v1/com.package.name/builds", {"tracks": [], "apks": []}, 400, "No payload"),
    (
        "/v1/com.package.name/builds",
        {
            "tracks": ["alpha"],
            "apks": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        400,
        "'media_body' is a required property",
    ),
    (
        "/v1/com.package.name/builds",
        {
            "tracks": ["alpha//////"],
            "bundles": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "greatest bundle",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        400,
        "Failed validating 'pattern' in schema['properties']['tracks']['items']",
    ),
    (
        "/v1/com.%20package.name/builds",
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
        400,
        "Invalid package name",
    ),
    (
        "/v1/com.package.name/builds",
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
            "apks": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "greatest apk",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        400,
        "Invalid payload. Cannot mix apks and bundles.",
    ),
]


@patch("android_store_service.resources.builds_resources.apks_logic")
@patch("android_store_service.resources.builds_resources.bundles_logic")
@pytest.mark.parametrize(
    "route,payload,exp_response_code,exp_response_message", negative_route_params
)
def test_negative_build_resources(
    bundles_logic_mock,
    apks_logic_mock,
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
    bundles_logic_mock.create_builds.assert_not_called()
    apks_logic_mock.create_builds.assert_not_called()


logic_negative_route_params = [
    (
        "/v1/invalid.package/builds",
        {
            "tracks": ["alpha"],
            "apks": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "greatest apk",
                    "deobfuscation_file": "1248765kjbskdf",
                }
            ],
        },
        Exception("Exception"),
        500,
        "Exception",
    ),
    (
        "/v1/invalid.package/builds",
        {
            "tracks": ["alpha"],
            "apks": [
                {
                    "sha1": "123",
                    "sha256": "090290",
                    "media_body": "greatest apk",
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


@patch("android_store_service.resources.builds_resources.apks_logic")
@pytest.mark.parametrize(
    "route,payload,exp_logic_response,exp_response_code,exp_response_message",
    logic_negative_route_params,
)
def test_logic_negative_response(
    apks_logic_mock,
    test_client,
    route,
    payload,
    exp_logic_response,
    exp_response_code,
    exp_response_message,
):
    apks_logic_mock.upload_apks.side_effect = [exp_logic_response]
    response = test_client.post(route, data=json.dumps(payload))
    assert response.status_code == exp_response_code
    assert exp_response_message in json.loads(response.data)["error"]["message"]

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

import pytest

from android_store_service import main


@pytest.fixture
def test_client():
    return main.app.test_client()


basic_route_params = [("v1/com.package.name/tracks", "com.package.name", 200)]


@patch("android_store_service.resources.tracks_resources.tracks_logic")
@pytest.mark.parametrize("route,package_name,exp_status_code", basic_route_params)
def test_tracks_list_resource(
    tracks_logic_mock, test_client, route, package_name, exp_status_code
):
    tracks_logic_mock.list_tracks.return_value = ["foo"]
    response = test_client.get(route)
    tracks_logic_mock.list_tracks.assert_called_once_with(package_name)
    assert response.status_code == exp_status_code
    assert json.loads(response.data) == {"tracks": ["foo"]}


negative_route_params = [
    ("v1/com.___bad_package_name!$param/tracks", 400, "Invalid package name")
]


@patch("android_store_service.resources.tracks_resources.tracks_logic")
@pytest.mark.parametrize(
    "route,exp_status_code,exp_response_message", negative_route_params
)
def test_tracks_list_resources_negative(
    tracks_logic_mock, test_client, route, exp_status_code, exp_response_message
):
    response = test_client.get(route)
    tracks_logic_mock.list_tracks.assert_not_called()
    assert response.status_code == exp_status_code
    assert json.loads(response.data)["error"]["message"] == exp_response_message


@patch("android_store_service.resources.tracks_resources.tracks_logic")
def test_tracks_list_resources_exception_propagation(tracks_logic_mock, test_client):
    tracks_logic_mock.list_tracks.side_effect = [Exception("Exception")]
    response = test_client.get("v1/com.package.namec/tracks")
    assert response.status_code == 500
    assert json.loads(response.data)["error"]["message"] == "Exception"

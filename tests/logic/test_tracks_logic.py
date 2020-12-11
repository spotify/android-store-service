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

from unittest.mock import Mock, patch

import pytest
from oauth2client import client

from android_store_service.logic import tracks_logic


@patch("android_store_service.logic.tracks_logic.GooglePlayBuildService")
def test_track_list_logic(service_mock):
    package_name = "com.package.name"
    list_tracks_return_value = ["foo"]
    edit_id = "foobar"

    gp_service_mock = Mock()
    gp_service_mock.create_edit.return_value = edit_id
    gp_service_mock.list_tracks.return_value = list_tracks_return_value
    service_mock.return_value = gp_service_mock

    results = tracks_logic.list_tracks(package_name)

    gp_service_mock.create_edit.assert_called_once_with()
    gp_service_mock.list_tracks.assert_called_once_with(edit_id)

    assert results == list_tracks_return_value


@patch("android_store_service.logic.tracks_logic.GooglePlayBuildService")
def test_track_list_logic_exception_propagation(service_mock):
    package_name = "com.package.name"
    gp_service_mock = Mock()
    gp_service_mock.create_edit.side_effect = [
        client.AccessTokenRefreshError("Exception")
    ]
    service_mock.return_value = gp_service_mock
    with pytest.raises(client.AccessTokenRefreshError):
        tracks_logic.list_tracks(package_name)
        gp_service_mock.create_edit.assert_called_once_with(package_name)
        gp_service_mock.list_tracks.assert_not_called()

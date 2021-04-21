# -*- coding: utf-8 -*-
# Copyright 2021 Spotify AB
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
from unittest.mock import patch
import pytest
import requests
from android_store_service.utils.bundle_adapter import adapt_bundle


@patch.object(requests, "get")
def test_adapt_bundle(mock_get):
    mock_get.return_value.content = b"contents of file"
    bundles = [
        {
            "sha256": "OTHUTNHE",
            "deobfuscation_file_link": "https://my_link",
            "media_body_link": "http://media_link",
        }
    ]
    assert adapt_bundle(bundles) == [
        {
            "sha256": "OTHUTNHE",
            "deobfuscation_file": "Y29udGVudHMgb2YgZmlsZQ==",
            "media_body": "Y29udGVudHMgb2YgZmlsZQ==",
        }
    ]


@patch.object(requests, "get")
def test_adapt_bundle_empty(mock_get):
    mock_get.return_value.content = b"contents of file"
    bundles = []
    assert adapt_bundle(bundles) == []


@patch.object(requests, "get")
def test_adapt_bundle_missing_key(mock_get):
    mock_get.return_value.content = b"contents of file"
    bundles = [
        {
            "no_sha256": "OTHUTNHE",
            "deobfuscation_file_link": "https://my_link",
            "media_body_link": "http://media_link",
        }
    ]
    with pytest.raises(KeyError):
        adapt_bundle(bundles)

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

from unittest.mock import patch, Mock

from android_store_service.utils import logging_utils


def test_setup_info_logging():
    app_config = {"LOGGING_LEVEL": "INFO"}
    logging_utils.setup_logging(app_config)
    assert logging.getLevelName(logging.root.level) == "INFO"


def test_setup_error_logging():
    app_config = {"LOGGING_LEVEL": "ERROR"}
    logging_utils.setup_logging(app_config)
    assert logging.getLevelName(logging.root.level) == "ERROR"


def create_mocked_request(status_code, text_value, raise_for_status, reason):
    patcher = patch("android_store_service.logging_utilities.requests.get")
    mock_response = Mock(status_code=status_code)
    mock_response.raise_for_status.side_effect = raise_for_status
    mock_response.text = text_value
    mock_response.reason = reason
    mock_request = patcher.start()
    mock_request.return_value = mock_response
    return mock_request


def test_get_request_id_no_context():
    assert logging_utils.get_request_id() == ""

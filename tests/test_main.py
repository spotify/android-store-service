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

import os
from unittest import mock
from unittest.mock import patch, MagicMock

from android_store_service import main


@mock.patch.dict(os.environ, {"RUNTEST": "True"})
@mock.patch.dict(main.app.config, {"LOCAL": False})
def test_runtest_on():
    main._check_run_test()
    assert main.app.config["LOCAL"] is True


@mock.patch.dict(main.app.config, {"LOCAL": False})
def test_runtest_off():
    with mock.patch.dict("os.environ"):
        if os.environ.get("RUNTEST"):  # this is used for tox runs.
            del os.environ["RUNTEST"]
        main._check_run_test()
        assert main.app.config["LOCAL"] is False


@patch("android_store_service.main.ffwd_metric")
def test_no_start_time(ffwd_mock):
    with main.app.test_request_context():
        main.send_request_metric(MagicMock())
        assert not ffwd_mock.called

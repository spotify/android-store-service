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
from os.path import join, dirname

import pytest

from android_store_service.utils import config_utils
from android_store_service.main import app


_TEST_DATA_PATH = join(dirname(__file__), "data")

positive_params = [("secret", "foobar\n"), ("empty_secret", "")]

negative_params = [
    (_TEST_DATA_PATH, "foobar"),
    (join(_TEST_DATA_PATH, "foobar"), "secret"),
]


@pytest.mark.parametrize("secret,exp_value", positive_params)
def test_secrets_positive(secret, exp_value):
    with app.app_context():
        app.config["SECRETS_PATH"] = _TEST_DATA_PATH
        assert exp_value == config_utils.get_secret(secret)
        assert exp_value == config_utils.get_secret(secret, path=_TEST_DATA_PATH)


@pytest.mark.parametrize("path,secret", negative_params)
def test_secrets_negative(path, secret):
    with app.app_context():
        app.config["SECRETS_PATH"] = path
        with pytest.raises(FileNotFoundError):
            config_utils.get_secret(secret)


secret_exists_params = [("secret", True), ("secret-does-not-exist", False)]


@pytest.mark.parametrize("secret,exp_value", secret_exists_params)
def test_secret_exists(secret, exp_value):
    with app.app_context():
        app.config["SECRETS_PATH"] = _TEST_DATA_PATH
        assert exp_value == config_utils.secret_exists(secret)
        assert exp_value == config_utils.secret_exists(secret, path=_TEST_DATA_PATH)

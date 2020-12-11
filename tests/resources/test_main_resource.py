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
import pytest

from android_store_service import main


@pytest.fixture
def test_client():
    return main.app.test_client()


basic_route_params = [("/status", 200, b'{\n  "status": "ok"\n}\n')]


@pytest.mark.parametrize("route,exp_code,exp_rsp_data", basic_route_params)
def test_basic_routes(test_client, route, exp_code, exp_rsp_data):
    rsp = test_client.get(route)

    assert rsp.status_code == exp_code
    assert rsp.data == exp_rsp_data

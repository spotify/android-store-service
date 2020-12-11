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

from flask import current_app


def read_file(conf_path):
    with open(str(conf_path), "r") as _file:
        return _file.read()


def get_secret(secret, path=None):
    if not path:
        path = current_app.config.get("SECRETS_PATH")
    file_path = f"{path}/{secret}"
    if not secret_exists(secret, path=path):
        raise FileNotFoundError(f"Secret {secret} does not exist at {file_path}")

    return read_file(file_path)


def secret_exists(secret, path=None):
    if not path:
        path = current_app.config.get("SECRETS_PATH")
    file_path = f"{path}/{secret}"
    if os.path.exists(file_path):
        return True
    return False

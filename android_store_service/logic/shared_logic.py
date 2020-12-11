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

import base64
import shutil
import tempfile


def create_temporary_directory():
    return tempfile.mkdtemp()


def store_base64_as_text_file(directory, content):
    fd, path = tempfile.mkstemp(dir=directory)
    with open(path, "w+") as f:
        f.write(base64.b64decode(content).decode("utf-8"))
    return path


def store_base64_as_binary_file(directory, b64_content):
    fd, path = tempfile.mkstemp(dir=directory)
    with open(path, "wb") as f:
        f.write(base64.decodebytes(b64_content.encode()))
    return path


def store_binaries_to_directory(directory, binaries):
    binary_paths = []
    for binary in binaries:
        binary_path = store_base64_as_binary_file(directory, binary["media_body"])

        deobfuscation_path = (
            store_base64_as_text_file(directory, binary["deobfuscation_file"])
            if binary.get("deobfuscation_file")
            else None
        )

        binary_paths.append(
            {"binary_path": binary_path, "deobfuscation_path": deobfuscation_path}
        )
    return binary_paths


def delete_temporary_dir(dir_path):
    shutil.rmtree(dir_path)

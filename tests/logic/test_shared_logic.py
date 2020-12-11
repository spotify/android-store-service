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

from unittest.mock import patch, mock_open, call

from android_store_service.logic import shared_logic


@patch("android_store_service.logic.shared_logic.tempfile")
def test_create_temporary_directory(tempfile_mock):

    expected_return_value = "/tmp/bar"
    tempfile_mock.mkdtemp.return_value = expected_return_value

    temp_dir_path = shared_logic.create_temporary_directory()

    tempfile_mock.mkdtemp.assert_called_once_with()
    assert temp_dir_path == expected_return_value


@patch("android_store_service.logic.shared_logic.tempfile")
def test_store_base64_as_text_file(tempfile_mock):
    temp_dir = "/tmp/foo"
    temp_file = "/tmp/foo/bar"
    tempfile_mock.mkstemp.return_value = 1, temp_file
    file_content = "SGVsbG8sIFdvcmxk"
    m = mock_open()
    with patch("android_store_service.logic.shared_logic.open", m, create=True):
        shared_logic.store_base64_as_text_file(temp_dir, file_content)
    m.assert_called_once_with(temp_file, "w+")
    tempfile_mock.mkstemp.assert_called_once_with(dir=temp_dir)
    handle = m()
    handle.write.assert_called_once_with("Hello, World")


@patch("android_store_service.logic.shared_logic.tempfile")
def test_store_base64_as_binary_file(tempfile_mock):
    temp_dir = "/tmp/foo"
    temp_file = "/tmp/foo/bar"
    tempfile_mock.mkstemp.return_value = 1, temp_file
    file_content = "SGVsbG8sIFdvcmxk"
    m = mock_open()
    with patch("android_store_service.logic.shared_logic.open", m, create=True):
        shared_logic.store_base64_as_binary_file(temp_dir, file_content)
    m.assert_called_once_with(temp_file, "wb")
    tempfile_mock.mkstemp.assert_called_once_with(dir=temp_dir)
    handle = m()
    handle.write.assert_called_once_with(b"Hello, World")


@patch("android_store_service.logic.shared_logic.store_base64_as_text_file")
@patch("android_store_service.logic.shared_logic.store_base64_as_binary_file")
def test_store_binaries_to_directory(store_binary_file_mock, store_text_file_mock):
    temp_dir = "/tmp/foo"
    store_binary_file_mock.side_effect = ["/tmp/foo/bar", "/tmp/foo/foobar"]
    store_text_file_mock.side_effect = ["/tmp/foo/bar.txt", "/tmp/foo/foobar.txt"]

    exp_result = [
        {"binary_path": "/tmp/foo/bar", "deobfuscation_path": "/tmp/foo/bar.txt"},
        {"binary_path": "/tmp/foo/foobar", "deobfuscation_path": "/tmp/foo/foobar.txt"},
    ]

    binary_list = [
        {"media_body": "binary_content_1", "deobfuscation_file": "text_content_1"},
        {"media_body": "binary_content_2", "deobfuscation_file": "text_content_2"},
    ]

    result = shared_logic.store_binaries_to_directory(temp_dir, binary_list)

    assert result == exp_result

    store_binary_file_mock.assert_has_calls(
        [call(temp_dir, "binary_content_1"), call(temp_dir, "binary_content_2")]
    )

    store_text_file_mock.assert_has_calls(
        [call(temp_dir, "text_content_1"), call(temp_dir, "text_content_2")]
    )

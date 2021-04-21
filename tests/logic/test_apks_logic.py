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
from unittest.mock import call, patch, Mock

import pytest
from googleapiclient.errors import HttpError

from android_store_service.logic import apks_logic
from tests.helpers.mock_utils import mock_httperror_content

temp_dir_mock_return_value = "/tmp/foo"
apk_path_mock = "/tmp/foo/bar.apk"
deobfuscation_path_mock = "/tmp/foo/bar.txt"

package_name = "com.package.name"
edit_id = "edit_id"

create_apks_params = [
    (
        ["alpha"],
        [{"media_body": "foo", "deobfuscation_file": "bar"}],
        [{"binary_path": apk_path_mock, "deobfuscation_path": deobfuscation_path_mock}],
        [call(edit_id, apk_path_mock)],
        [1],
        [call(edit_id, 1, deobfuscation_path_mock)],
        [call(edit_id, [1], "alpha")],
    ),
    (
        ["alpha", "beta"],
        [
            {"media_body": "foo", "deobfuscation_file": "bar"},
            {"media_body": "foobar", "deobfuscation_file": "barfoo"},
        ],
        [
            {
                "binary_path": apk_path_mock,
                "deobfuscation_path": deobfuscation_path_mock,
            },
            {
                "binary_path": apk_path_mock,
                "deobfuscation_path": deobfuscation_path_mock,
            },
        ],
        [call(edit_id, apk_path_mock), call(edit_id, apk_path_mock)],
        [2, 3],
        [
            call(edit_id, 2, deobfuscation_path_mock),
            call(edit_id, 3, deobfuscation_path_mock),
        ],
        [call(edit_id, [2, 3], "alpha"), call(edit_id, [2, 3], "beta")],
    ),
    (
        ["alpha", "beta"],
        [
            {"media_body": "foo", "deobfuscation_file": "bar"},
            {"media_body": "foobar", "deobfuscation_file": ""},
        ],
        [
            {
                "binary_path": apk_path_mock,
                "deobfuscation_path": deobfuscation_path_mock,
            },
            {"binary_path": apk_path_mock, "deobfuscation_path": None},
        ],
        [call(edit_id, apk_path_mock), call(edit_id, apk_path_mock)],
        [2, 3],
        [call(edit_id, 2, deobfuscation_path_mock)],
        [call(edit_id, [2, 3], "alpha"), call(edit_id, [2, 3], "beta")],
    ),
]


@patch("android_store_service.logic.apks_logic.shared_logic")
@patch("android_store_service.logic.apks_logic.GooglePlayBuildService")
@pytest.mark.parametrize(
    "tracks,"
    "apks,"
    "store_binaries_return_value,"
    "exp_upload_apk_calls,"
    "upload_apks_side_effects,"
    "exp_upload_deobfuscation_calls,"
    "exp_promote_to_track_calls",
    create_apks_params,
)
def test_create_builds_apks(
    android_store_service_mock,
    shared_logic_mock,
    tracks,
    apks,
    store_binaries_return_value,
    exp_upload_apk_calls,
    upload_apks_side_effects,
    exp_upload_deobfuscation_calls,
    exp_promote_to_track_calls,
):

    gp_service_mock = Mock()
    shared_logic_mock.create_temporary_directory.return_value = (
        temp_dir_mock_return_value
    )

    android_store_service_mock.return_value = gp_service_mock
    gp_service_mock.create_edit.return_value = edit_id
    gp_service_mock.upload_apk.side_effect = upload_apks_side_effects
    shared_logic_mock.store_binaries_to_directory.return_value = (
        store_binaries_return_value
    )

    apks_logic.upload_apks(package_name, tracks, apks, False)

    shared_logic_mock.store_binaries_to_directory.called_once_with(
        temp_dir_mock_return_value, apks
    )

    gp_service_mock.upload_apk.assert_has_calls(exp_upload_apk_calls)
    gp_service_mock.upload_deobfuscation_file.assert_has_calls(
        exp_upload_deobfuscation_calls
    )
    gp_service_mock.promote_to_track.assert_has_calls(exp_promote_to_track_calls)
    gp_service_mock.validate_edit.assert_called_once_with(edit_id)
    gp_service_mock.commit_edit.assert_called_once_with(edit_id)
    shared_logic_mock.delete_temporary_dir.assert_called_once_with(
        temp_dir_mock_return_value
    )


@patch("android_store_service.logic.apks_logic.shared_logic")
@patch("android_store_service.logic.apks_logic.GooglePlayBuildService")
def test_upload_apk_dry_run(android_store_service_mock, shared_logic_mock):
    gp_service_mock = Mock()
    shared_logic_mock.create_temporary_directory.return_value = (
        temp_dir_mock_return_value
    )
    android_store_service_mock.return_value = gp_service_mock

    gp_service_mock.upload_apk.return_value = 1337
    shared_logic_mock.store_binaries_to_directory.return_value = [
        {"binary_path": apk_path_mock, "deobfuscation_path": deobfuscation_path_mock}
    ]

    apks_logic.upload_apks(
        package_name,
        ["alpha"],
        [{"media_body": "123", "deobfuscation_file": "123"}],
        True,
    )

    gp_service_mock.commit_edit.assert_not_called()


upload_apk_exception_params = [
    (Exception("error")),
    (
        HttpError(
            {},
            json.dumps(
                mock_httperror_content(
                    404, "APK specifies a version code that has already been used."
                )
            ).encode("utf-8"),
        )
    ),
    (
        HttpError(
            {},
            json.dumps(
                mock_httperror_content(
                    403, "Some other error message but with same status code."
                )
            ).encode("utf-8"),
        )
    ),
    (HttpError({}, json.dumps({"foo": "bar"}).encode("utf-8"))),
    (HttpError({}, "Error is not JSON format".encode("utf-8"))),
    (HttpError({}, "".encode("utf-8"))),
]


@patch("android_store_service.logic.apks_logic.shared_logic")
@patch("android_store_service.logic.apks_logic.GooglePlayBuildService")
@pytest.mark.parametrize("exc", upload_apk_exception_params)
def test_upload_apk_exception(android_store_service_mock, shared_logic_mock, exc):
    gp_service_mock = Mock()
    shared_logic_mock.create_temporary_directory.return_value = (
        temp_dir_mock_return_value
    )
    android_store_service_mock.return_value = gp_service_mock
    gp_service_mock.upload_apk.side_effect = [exc]
    shared_logic_mock.store_binaries_to_directory.return_value = [
        {"binary_path": apk_path_mock, "deobfuscation_path": deobfuscation_path_mock}
    ]

    with pytest.raises(exc.__class__):
        apks_logic.upload_apks(package_name, ["alpha"], [{"apk"}], False)
    gp_service_mock.upload_deobfuscation_file.assert_not_called()
    shared_logic_mock.delete_temporary_dir.assert_called_once_with(
        temp_dir_mock_return_value
    )
    gp_service_mock.promote_to_track.assert_not_called()
    gp_service_mock.commit_edit.assert_not_called()


@patch("android_store_service.logic.apks_logic.shared_logic")
@patch("android_store_service.logic.apks_logic.GooglePlayBuildService")
def test_upload_apk_duplicate(android_store_service_mock, shared_logic_mock):
    gp_service_mock = Mock()
    shared_logic_mock.create_temporary_directory.return_value = (
        temp_dir_mock_return_value
    )
    android_store_service_mock.return_value = gp_service_mock
    gp_service_mock.upload_apk.side_effect = [
        HttpError(
            {},
            json.dumps(
                mock_httperror_content(
                    403, "APK specifies a version code that has already been used."
                )
            ).encode("utf-8"),
        )
    ]
    shared_logic_mock.store_binaries_to_directory.return_value = [
        {"binary_path": apk_path_mock, "deobfuscation_path": deobfuscation_path_mock}
    ]

    res = apks_logic.upload_apks(package_name, ["alpha"], [{"apk"}], False)
    assert [] == res
    gp_service_mock.upload_deobfuscation_file.assert_not_called()
    shared_logic_mock.delete_temporary_dir.assert_called_once_with(
        temp_dir_mock_return_value
    )
    gp_service_mock.promote_to_track.assert_not_called()
    gp_service_mock.commit_edit.assert_not_called()

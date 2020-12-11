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

from unittest.mock import patch, MagicMock, Mock

import pytest

from android_store_service import googleplay_build_service
from android_store_service.googleplay_build_service import GooglePlayBuildService
from android_store_service.utils import config_utils

package_name = "com.package.name"
edit_id = "edit_id"
track = "alpha"
version_code = 10000
version_codes = [version_code]


def setup_mocked_build_service(execute_return_value):
    execute_mock = MagicMock(
        return_value=MagicMock(execute=MagicMock(return_value=execute_return_value))
    )

    tracks_mock = MagicMock(
        return_value=MagicMock(update=execute_mock, list=execute_mock)
    )

    apks_mock = MagicMock(return_value=MagicMock(upload=execute_mock))

    bundles_mock = MagicMock(return_value=MagicMock(upload=execute_mock))

    deobfuscation_files_mock = MagicMock(return_value=MagicMock(upload=execute_mock))

    edits_mock = MagicMock(
        return_value=MagicMock(
            tracks=tracks_mock,
            insert=execute_mock,
            validate=execute_mock,
            apks=apks_mock,
            bundles=bundles_mock,
            deobfuscationfiles=deobfuscation_files_mock,
        )
    )

    build_publisher_mock = MagicMock(edits=edits_mock)

    return build_publisher_mock


build_publisher_params = [
    (True, [True, True], f"{package_name}-viewer"),
    (True, [True, False], package_name),
    (True, [False, True], "googleplayapiaccess-viewer"),
    (True, [False, False], "googleplayapiaccess"),
    (False, [True], package_name),
    (False, [False], "googleplayapiaccess"),
]


@patch.object(googleplay_build_service, "ServiceAccountCredentials")
@patch.object(googleplay_build_service, "httplib2")
@patch.object(googleplay_build_service, "build")
@patch.object(config_utils, "get_secret")
@patch.object(config_utils, "secret_exists")
@pytest.mark.parametrize(
    "is_viewer,secret_exists_rsp,exp_secret", build_publisher_params
)
def test_build_publisher_service(
    secret_exists_mock,
    secret_mock,
    build_mock,
    httplib2_mock,
    service_account_credentials_mock,
    is_viewer,
    secret_exists_rsp,
    exp_secret,
):
    scopes = ["https://www.googleapis.com/auth/androidpublisher"]
    secret_exists_mock.side_effect = secret_exists_rsp
    secret_mock.return_value = '{"secret": "content"}'
    httplib2_return_value = "http-return value"
    authorize_return_value = "authorize_return_value"

    httplib2_mock.Http.return_value = httplib2_return_value
    credentials_mock = Mock()
    credentials_mock.authorize.return_value = authorize_return_value

    service_account_credentials_mock.from_json_keyfile_dict.return_value = (
        credentials_mock
    )

    GooglePlayBuildService(package_name, viewer=is_viewer)

    secret_mock.assert_called_once_with(exp_secret)

    service_account_credentials_mock.from_json_keyfile_dict.assert_called_once_with(
        {"secret": "content"}, scopes
    )

    credentials_mock.authorize.assert_called_once_with(httplib2_return_value)

    build_mock.assert_called_once_with(
        "androidpublisher", "v3", http=authorize_return_value, cache_discovery=False
    )


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_create_edit(build_publisher_mock):
    execute_return_value = {"id": edit_id}

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    result = googleplay_service.create_edit()

    build_publisher_service_mock.edits().insert.assert_called_once_with(
        body={}, packageName=package_name
    )
    build_publisher_service_mock.edits().insert().execute.assert_called_once()

    assert result == edit_id


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_promote_to_track(build_publisher_mock):
    execute_return_value = {"version_codes": version_codes, "track": track}

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    body = {
        "track": track,
        "releases": [{"status": "completed", "versionCodes": version_codes}],
    }

    googleplay_service = GooglePlayBuildService(package_name)
    result = googleplay_service.promote_to_track(edit_id, version_codes, track)

    build_publisher_service_mock.edits().tracks().update.assert_called_once_with(
        editId=edit_id, track=track, packageName=package_name, body=body
    )

    build_publisher_service_mock.edits().tracks().update().execute.assert_called_once()

    assert result == execute_return_value


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_validate_edit(build_publisher_mock):
    execute_return_value = {"version_codes": version_codes, "track": track}

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    googleplay_service.validate_edit(edit_id)

    build_publisher_service_mock.edits().validate.assert_called_once_with(
        editId=edit_id, packageName=package_name
    )
    build_publisher_service_mock.edits().validate().execute.assert_called_once()


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_commit_edit(build_publisher_mock):
    execute_return_value = {"version_codes": version_codes, "track": track}

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    googleplay_service.commit_edit(edit_id)

    build_publisher_service_mock.edits().commit.assert_called_once_with(
        editId=edit_id, packageName=package_name
    )
    build_publisher_service_mock.edits().commit().execute.assert_called_once()


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_upload_apk(build_publisher_mock):
    execute_return_value = {"versionCode": version_code}
    apk_file = "apk_file"

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    response = googleplay_service.upload_apk(edit_id, apk_file)

    build_publisher_service_mock.edits().apks().upload.assert_called_once_with(
        media_mime_type="application/octet-stream",
        editId=edit_id,
        packageName=package_name,
        media_body=apk_file,
    )
    build_publisher_service_mock.edits().apks().upload().execute.assert_called_once()

    assert response == version_code


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_upload_bundle(build_publisher_mock):
    execute_return_value = {"versionCode": version_code}
    bundle_file = "bundle_file"

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    response = googleplay_service.upload_bundle(edit_id, bundle_file)

    build_publisher_service_mock.edits().bundles().upload.assert_called_once_with(
        media_mime_type="application/octet-stream",
        editId=edit_id,
        packageName=package_name,
        media_body=bundle_file,
    )
    build_publisher_service_mock.edits().bundles().upload().execute.assert_called_once()

    assert response == version_code


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_list_tracks(build_publisher_mock):
    execute_return_value = {"tracks": ["foo", "bar"]}

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    response = googleplay_service.list_tracks(edit_id)

    build_publisher_service_mock.edits().tracks().list.assert_called_once_with(
        editId=edit_id, packageName=package_name
    )
    build_publisher_service_mock.edits().tracks().list().execute.assert_called_once()

    assert response == ["foo", "bar"]


@patch.object(
    googleplay_build_service.GooglePlayBuildService, "build_publisher_service"
)
def test_upload_deobfuscation_file(build_publisher_mock):
    execute_return_value = {"deobfuscationFile": ["foo", "bar"]}

    deobfuscation_file_path = "path/to/file"
    version_code = 1

    build_publisher_service_mock = setup_mocked_build_service(execute_return_value)

    build_publisher_mock.return_value = build_publisher_service_mock

    googleplay_service = GooglePlayBuildService(package_name)
    response = googleplay_service.upload_deobfuscation_file(
        edit_id, version_code, deobfuscation_file_path
    )

    build_publisher_service_mock.edits().deobfuscationfiles().upload.assert_called_once_with(
        editId=edit_id,
        packageName=package_name,
        apkVersionCode=version_code,
        deobfuscationFileType="proguard",
        media_mime_type="application/octet-stream",
        media_body=deobfuscation_file_path,
    )
    build_publisher_service_mock.edits().tracks().list().execute.assert_called_once()

    assert response == ["foo", "bar"]

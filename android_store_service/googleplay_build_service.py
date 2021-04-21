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

import httplib2

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from android_store_service.utils import config_utils

_NUM_RETRIES = 3


class GooglePlayBuildService:
    def __init__(self, package_name, viewer=False):
        """
        Service for communicating with the Google Play Developer API.

        :param package_name: The package name for the app, e.g. com.package.name
        :param viewer: (Optional) True if data will only be viewed (e.g. list tracks),
            False if data will be edited (e.g. upload binary).
        """
        self.package_name = package_name
        self.service = self.build_publisher_service(viewer)

    def build_publisher_service(self, viewer):
        scopes = ["https://www.googleapis.com/auth/androidpublisher"]
        secret = self._select_secret(viewer)
        secrets = json.loads(config_utils.get_secret(secret))
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scopes)
        http = credentials.authorize(httplib2.Http())
        return build("androidpublisher", "v3", http=http, cache_discovery=False)

    def _select_secret(self, viewer):
        if config_utils.secret_exists(self.package_name):
            if viewer and config_utils.secret_exists(f"{self.package_name}-viewer"):
                return f"{self.package_name}-viewer"
            return self.package_name
        else:
            if viewer and config_utils.secret_exists("googleplayapiaccess-viewer"):
                return "googleplayapiaccess-viewer"
            return "googleplayapiaccess"

    def create_edit(self):
        edit_request = self.service.edits().insert(
            body={}, packageName=self.package_name
        )
        result = edit_request.execute(num_retries=_NUM_RETRIES)
        return result["id"]

    def promote_to_track(self, edit_id, version_codes, track):
        body = {
            "track": track,
            "releases": [{"status": "completed", "versionCodes": version_codes}],
        }
        return (
            self.service.edits()
            .tracks()
            .update(
                editId=edit_id, track=track, packageName=self.package_name, body=body
            )
            .execute(num_retries=_NUM_RETRIES)
        )

    def validate_edit(self, edit_id):
        validate_request = (
            self.service.edits()
            .validate(editId=edit_id, packageName=self.package_name)
            .execute(num_retries=_NUM_RETRIES)
        )
        return validate_request

    def commit_edit(self, edit_id):
        commit_request = (
            self.service.edits()
            .commit(editId=edit_id, packageName=self.package_name)
            .execute(num_retries=_NUM_RETRIES)
        )
        return commit_request

    def upload_apk(self, edit_id, apk_file_path):
        apk_response = (
            self.service.edits()
            .apks()
            .upload(
                media_mime_type="application/octet-stream",
                editId=edit_id,
                packageName=self.package_name,
                media_body=apk_file_path,
            )
            .execute(num_retries=_NUM_RETRIES)
        )
        return apk_response["versionCode"]

    def upload_bundle(self, edit_id, bundle_file_path):
        bundle_response = (
            self.service.edits()
            .bundles()
            .upload(
                media_mime_type="application/octet-stream",
                editId=edit_id,
                packageName=self.package_name,
                media_body=bundle_file_path,
            )
            .execute(num_retries=_NUM_RETRIES)
        )
        return bundle_response["versionCode"]

    def list_tracks(self, edit_id):
        tracks_response = (
            self.service.edits()
            .tracks()
            .list(editId=edit_id, packageName=self.package_name)
            .execute(num_retries=_NUM_RETRIES)
        )
        return tracks_response["tracks"]

    def upload_deobfuscation_file(self, edit_id, version_code, deobfuscation_file):
        deobfuscation_response = (
            self.service.edits()
            .deobfuscationfiles()
            .upload(
                editId=edit_id,
                packageName=self.package_name,
                apkVersionCode=version_code,
                deobfuscationFileType="proguard",
                media_mime_type="application/octet-stream",
                media_body=deobfuscation_file,
            )
            .execute(num_retries=_NUM_RETRIES)
        )
        return deobfuscation_response["deobfuscationFile"]

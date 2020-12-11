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
import logging

from googleapiclient.errors import HttpError

from android_store_service.googleplay_build_service import GooglePlayBuildService
from android_store_service.logic import shared_logic


def upload_bundles(package_name, tracks, bundles, dry_run):

    version_codes = []

    temporary_build_directory = shared_logic.create_temporary_directory()
    try:

        bundles_to_upload = shared_logic.store_binaries_to_directory(
            temporary_build_directory, bundles
        )

        google_play_service = GooglePlayBuildService(package_name)
        edit_id = google_play_service.create_edit()

        for bundle_to_upload in bundles_to_upload:

            version_code = google_play_service.upload_bundle(
                edit_id, bundle_to_upload["binary_path"]
            )

            if bundle_to_upload["deobfuscation_path"]:
                google_play_service.upload_deobfuscation_file(
                    edit_id, version_code, bundle_to_upload["deobfuscation_path"]
                )

            version_codes.append(version_code)

        for track in tracks:
            google_play_service.promote_to_track(edit_id, version_codes, track)

        google_play_service.validate_edit(edit_id)
        if not dry_run:
            google_play_service.commit_edit(edit_id)
    except HttpError as err:
        message = "APK specifies a version code that has already been used."
        error = json.loads(err.content)["error"]
        if error["code"] == 403 and error["message"] == message:
            logging.info(message)
        else:
            raise err
    finally:
        shared_logic.delete_temporary_dir(temporary_build_directory)

    return version_codes

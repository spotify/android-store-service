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

from android_store_service.googleplay_build_service import GooglePlayBuildService


def list_tracks(package_name):
    google_play_service = GooglePlayBuildService(package_name, viewer=True)
    edit_id = google_play_service.create_edit()
    return google_play_service.list_tracks(edit_id)

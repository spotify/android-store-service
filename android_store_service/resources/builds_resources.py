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

import re
import logging

import jsonschema
from flask import Blueprint, request, jsonify
from jsonschema import ValidationError

from android_store_service.logic import bundles_logic, apks_logic
from android_store_service.exceptions import BadRequestException

builds_blueprint = Blueprint("builds-blueprint", __name__)


@builds_blueprint.route("/<package_name>/builds", methods=["POST"])
def create_builds(package_name):
    if not re.match(r"^[a-zA-Z0-9\.]+$", package_name):
        raise BadRequestException("Invalid package name")

    data = request.get_json(force=True)
    try:
        jsonschema.validate(data, builds_schema)
    except ValidationError as e:
        raise BadRequestException(str(e))

    tracks = data.get("tracks", [])
    bundles = data.get("bundles", [])
    apks = data.get("apks", [])
    dry_run = data.get("dry_run", False)

    if not bundles and not apks:
        if not tracks:
            raise BadRequestException("No payload")
        raise BadRequestException("No binaries")
    if bundles and apks:
        raise BadRequestException("Invalid payload. Cannot mix apks and bundles.")
    if bundles:
        version_codes = bundles_logic.upload_bundles(
            package_name, tracks, bundles, dry_run
        )
    else:
        version_codes = apks_logic.upload_apks(package_name, tracks, apks, dry_run)
    logging.info(
        f"Successfully uploaded new binaries for {package_name} to google play. "
        f'Tracks: {", ".join(tracks)}. '
        f'Version codes: {", ".join(str(x) for x in version_codes)}'
    )
    return jsonify(version_codes)


builds_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Upload apks or bundles to google play schema",
    "type": "object",
    "properties": {
        "tracks": {
            "type": "array",
            "minItems": 0,
            "items": {"type": "string", "pattern": r"^[a-zA-Z0-9\:\s]+$"},
        },
        "bundles": {
            "type": "array",
            "minItems": 0,
            "items": {
                "type": "object",
                "required": ["sha1", "sha256", "media_body"],
                "properties": {
                    "sha1": {"type": "string"},
                    "sha256": {"type": "string"},
                    "media_body": {"type": "string"},
                    "deobfuscation_file": {"type": "string"},
                },
            },
        },
        "apks": {
            "type": "array",
            "minItems": 0,
            "items": {
                "type": "object",
                "required": ["sha1", "sha256", "media_body"],
                "properties": {
                    "sha1": {"type": "string"},
                    "sha256": {"type": "string"},
                    "media_body": {"type": "string"},
                    "deobfuscation_file": {"type": "string"},
                },
            },
        },
        "dry_run": {"type": "boolean"},
    },
}

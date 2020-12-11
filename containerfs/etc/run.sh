#!/bin/bash -ex

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


#Setup uwsgi socket, log, pid directories and permissions
mkdir -p /var/log/uwsgi/app
mkdir -p /var/run/uwsgi/app/android-store-service
chown -R www-data:www-data /var/run/uwsgi/app
export ENV APP_CONFIG_FILE=/etc/config/default/androidstoreservice.py


mkdir -p /etc/uwsgi/apps-enabled
ln -sf /etc/uwsgi/apps-available/android-store-service.ini /etc/uwsgi/apps-enabled/android-store-service.ini

uwsgi --ini /etc/uwsgi/apps-enabled/android-store-service.ini

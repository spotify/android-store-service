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

FROM ubuntu:18.04

RUN apt-get update && apt-get install  --yes  --allow-remove-essential --no-install-recommends \
curl \
apt-transport-https \
gnupg \
debian-keyring \
debian-archive-keyring \
software-properties-common

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys AA8E81B4331F7F50
RUN add-apt-repository main
# Get latest stable version of nginx that has remote syslog logging support
RUN echo "deb http://nginx.org/packages/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN echo "deb http://security.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list
RUN echo "deb-src  http://security.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list
RUN echo "deb-src http://nginx.org/packages/ubuntu/ trusty nginx" >> /etc/apt/sources.list
RUN curl -s http://nginx.org/keys/nginx_signing.key | apt-key add -

# Install the things
RUN apt-get update && apt-get install --yes  --allow-remove-essential --no-install-recommends \
  g++ \
  gettext \
  jq \
  libssl1.0.0 \
  nginx \
  python3.6-dev \
  python3-venv \
  rsyslog \
  supervisor \
  && rm -rf /var/lib/apt/lists/*

# Define Workspace
ENV WORKDIR /usr/src/app
WORKDIR /usr/src/app
RUN mkdir -p /usr/src/app

# Environment Variables
ENV PYTHONPATH $WORKDIR
ENV VENV $WORKDIR/.venv
ENV PATH $VENV/bin:$PATH

COPY containerfs /

# Copy files
COPY README.md /usr/src/app
COPY requirements.txt /usr/src/app
COPY setup.* /usr/src/app/
COPY test-requirements.txt /usr/src/app
COPY tox.ini /usr/src/app

RUN python3.6 -m venv /usr/src/app/.venv

# https://github.com/GoogleCloudPlatform/google-cloud-python/issues/2990
RUN mkdir -p /var/log/supervisord
RUN /usr/src/app/.venv/bin/pip install --upgrade setuptools
RUN /usr/src/app/.venv/bin/pip install wheel
RUN /usr/src/app/.venv/bin/pip install -r requirements.txt -i https://pypi.org/simple
RUN /usr/src/app/.venv/bin/pip install uwsgi

# Copy app code
COPY android_store_service /usr/src/app/android_store_service
COPY tests/ /usr/src/app/tests

EXPOSE 8080

CMD ["supervisord", "-n"]

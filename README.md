# Android Store Service

This is a service that uploads APKs and bundles to Google Play Store. It is built to use together with [Backstage](https://backstage.io/), but can also be used as a standalone service.



## Credentials
In order to use this service, you must create Service Accounts linked to your Google Play Console project. 
For instructions on how to generate a service account, or more details regarding the API, please refer to [Google Play Developer API documentation](https://developers.google.com/android-publisher/getting_started#using_a_service_account).

When the Service Account is acquired, specify the path to its secret through setting `SECRETS_PATH` in `containerfs/etc/config/default/androidstoreservice.py`. The default for `SECRETS_PATH` is `/etc/secrets/`, however, that can be changed if another path is preferred. 

There are two config-files. The first is called `default_config.py` and is located in `/config`. It is used for local development. The other one is called `androidstoreservice.py` and is located in `/containerfs/etc/default/`. That one is used in production. Both config files contain variables that can to be customized to fit your own project.

The service lets you use different service accounts - one for uploading, for example `androidstoreservice.json`, and another for viewing, e.g., `androidstoreservice-viewer.json`. The viewer account is just used for viewing eligible data in the Google Play Store, whereas the other service account is used for editing assets.

The `METRICS_KEY` should point to your GCP project if you use [shumway](https://github.com/spotify/shumway)

## API

### Builds
```
POST v1/<package_name>/builds
```
This endpoint is used to upload a new binary to Google Play Store, and promotes it to a track e.g., Alpha.
The body holds the following format:
```
{
    "tracks": List of tracks, e.g. ["alpha"] (Optional),
    "apks": [
        {
            "sha1": sha1 sum of the apk (string),
            "sha256": sha256 sum of the apk (string),
            "media_body": Base64 encoded apk (string),
            "deobfuscation_file": Base 64 encoded deobfuscation file, also known as mapping file (string)
        }
    ],
    "bundles": [
        {
            "sha1": sha1 sum of the bundle (string),
            "sha256": sha256 sum of the bundle (string),
            "media_body": Base64 encoded bundle (string),
            "deobfuscation_file": Base 64 encoded deobfuscation file, also known as mapping file (string)
        }
    ],
}
```
```POST v1/<package_name>/apks```
This endpoint uploads APKs. There is an option of dry running the request - the service validates the commit against Google Play Store, but does not upload it if "dry_run" is set to True. The body holds the following format:
```
{
  "tracks": List of tracks, e.g., ["alpha"](Optional),
  "apk": [
          {
            "sha1": sha1 sum of the apk (string),
            "sha256": sha256 sum of the apk (string),
            "media_body": Base64 encoded apk (string),
            "deobfuscation_file": Base 64 encoded deobfuscation file, also known as mapping file (string)
        }
  ]
  "dry_run": True or False(boolean, Optional)
}
```
```POST v1/<package_name>/bundles```
This endpoint uploads bundles. There is an option of dry running the request- the service validates the commit against Google Play Store, but does not upload it if "dry_run" is set to True. The body holds the following format:
```
{
  "tracks": List of tracks, e.g., ["alpha"](Optional),
  "bundles": [
          {
            "sha1": sha1 sum of the apk (string),
            "sha256": sha256 sum of the apk (string),
            "media_body": Base64 encoded apk (string),
            "deobfuscation_file": Base 64 encoded deobfuscation file, also known as mapping file (string)
        }
  ]
  "dry_run": True or False(boolean, Optional)
}
```
This endpoint will list all your current tracks that you have on Google Play Console
```GET v1/<package_name>/tracks```

### Usage

Easiest way to deploy the app is through our image on Docker Hub
```
docker run spotify/android_store_service:latest
```


### Setup local development

#### Create virtual environment
Install virtualenvwrapper:
```
brew install python (or preferably using [pyenv](https://github.com/pyenv/pyenv)
/usr/local/bin/pip install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
```

```
mkvirtualenv --python=`which python3` <name>
```

#### Install requirements
While working in a virtual environment run:
```
pip install -r requirements.txt
```

#### Run tests locally
```
tox
```

### Contributing
We would really appreciate if you have any improvements that can be added to the service!

Make sure to follow the [GitHub Flow Workflow](https://guides.github.com/introduction/flow/):

1. Fork the project
2. Check out the master branch
3. Create a feature branch
4. Write code and tests for your change
5. From your branch, make a pull request against this repos master branch
6. Work with [repo maintainers](OWNERS.md) to get your change reviewed
7. Wait for your change to be pulled into the master branch
8. Delete your feature branch

#### Good first issues
* Add extra functionality and endpoints for other parts of the Google Play API
* Look at "Click to Deploy" implementations
* Allow for configuration of metrics exporter (currently the service uses ffwd and [shumway](https://github.com/spotify/shumway))

### Code of Conduct
This project adheres to the [Open Code of Conduct][code-of-conduct]. By participating, you are expected to honor this code.

[code-of-conduct]: https://github.com/spotify/code-of-conduct/blob/master/code-of-conduct.md
### License
Copyright 2020 Spotify AB.

Licensed under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0

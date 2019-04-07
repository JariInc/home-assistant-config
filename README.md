# My Home Assistant setup

ToDo: write this readme

[![Build Status](https://travis-ci.org/JariInc/home-assistant-config.svg?branch=master)](https://travis-ci.org/JariInc/home-assistant-config)

## Restoring backup

```bash
docker run -it --rm wernight/duplicity:latest /bin/sh
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export S3_USE_SIGV4=true
mkdir -p /tmp/restore
duplicity --no-encryption -t [restore time, for example 2D] --file-to-restore [restored_file] s3://s3.eu-central-1.amazonaws.com/p16-hass-backup/hass /tmp/restore/[restored_file]
```
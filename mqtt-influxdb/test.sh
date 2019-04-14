#!/bin/sh

IMAGE=mqtt-influxdb-test:latest

docker build --rm=false --tag $IMAGE .
docker run --rm $IMAGE pytest --log-cli-level=debug
docker rmi $IMAGE
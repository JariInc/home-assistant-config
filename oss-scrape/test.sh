#!/bin/sh

IMAGE=oss-scrape-test:latest

# docker build --rm=false --tag $IMAGE .
# docker run --rm $IMAGE pytest --log-cli-level=debug
# docker rmi $IMAGE

 docker build -t $IMAGE .
 docker run -it --rm --mount type=bind,src=/hass/oss-scrape,dst=/usr/src/app $IMAGE sh
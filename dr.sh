#!/usr/bin/env bash

CONTAINER_TAG=bindings-crashes

set -e

echo "Building $CONTAINER_TAG container..."

docker build -t ${CONTAINER_TAG} --file docker/Dockerfile .

echo "Launching $CONTAINER_TAG container..."

docker run -it --rm --mount type=bind,source="$PWD",target=/home/tester/crashes ${CONTAINER_TAG}

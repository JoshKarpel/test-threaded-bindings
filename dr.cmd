@echo off

SET CONTAINER_TAG=bindings-crashes

ECHO Building %CONTAINER_TAG% container...

docker build -t %CONTAINER_TAG% --file docker/Dockerfile .

ECHO Launching %CONTAINER_TAG% container...

docker run -it --rm --mount type=bind,source="%CD%",target=/home/tester/crashes %CONTAINER_TAG%

#!/bin/bash

# Build docker image
docker build --no-cache -t andreu_timelens:latest -f Dockerfile .
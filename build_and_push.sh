#!/usr/bin/env bash

# This script shows how to build the Docker image and push it to ECR to be ready for use
# by SageMaker.

# The argument to this script is the image name. This will be used as the image on the local
# machine and combined with the account and region to form the repository name for ECR.
image="ryanc2811/recommender"

if [ "$image" == "" ]
then
    echo "Usage: $0 <image-name>"
    exit 1
fi


docker build  -t ${image} .

docker run -p 8080:80 --name recommender_api --restart always "ryanc2811/recommender"
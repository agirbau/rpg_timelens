#!/bin/bash

docker rm andreu_timelens
docker run \
    --shm-size=1g \
    --name andreu_timelens \
    -it \
    -v /home/andreu/work/projects/research/methods/rpg_timelens:/home/user/app \
    -v /home/andreu/datasets:/home/user/datasets \
    -v /home/andreu/work/andreu_utils:/home/user/global_utils \
    andreu_timelens
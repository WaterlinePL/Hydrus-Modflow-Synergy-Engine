#!/bin/bash
# Scripts is meant to be used while in root of repo

docker build -t watermodelling/hydrus-modflow-synergy-engine:water-modelling-standalone -f Dockerfile.docker .
docker push watermodelling/hydrus-modflow-synergy-engine:water-modelling-standalone